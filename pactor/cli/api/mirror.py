import pydantic
import os
import sys
import urllib.request
import threading
import libtorrent
import time
import asyncio
from enum import Enum
from fastapi import HTTPException
from fastapi.responses import FileResponse

from .main import app
from ...session import session
from ...config import config
from ...__init__ import __version__


class Repos(Enum):
	core = 'core'
	extra = 'extra'
	community = 'community'
	multilib = 'multilib'

class Databases(Enum):
	core = 'core.db'
	extra = 'extra.db'
	community = 'community.db'
	multilib = 'multilib.db'

class Archives(Enum):
	core = 'core.db.tar.gz'
	extra = 'extra.db.tar.gz'
	community = 'community.db.tar.gz'
	multilib = 'multilib.db.tar.gz'

class Signatures(Enum):
	core = 'core.db.sig'
	extra = 'extra.db.sig'
	community = 'community.db.sig'
	multilib = 'multilib.db.sig'

class Architectures(Enum):
	x86_64 = 'x86_64'

class RepoDatabase(pydantic.BaseModel):
	repo :Repos
	arch :Architectures
	database :Databases

class RepoArchive(pydantic.BaseModel):
	repo :Repos
	arch :Architectures
	database :Archives

class RepoSignatures(pydantic.BaseModel):
	repo :Repos
	arch :Architectures
	database :Signatures

class Package(pydantic.BaseModel):
	repo :Repos
	arch :Architectures
	package :str

@app.get("/{repo}/{arch}/{database}.db")
async def get_db(repo :str, arch :str, database :str):
	requested = RepoDatabase(repo=Repos[repo], arch=Architectures[arch], database=Databases[database])

	(config.cache_dir / requested.repo.value / "os" / requested.arch.value).mkdir(parents=True, exist_ok=True)

	if (static_file := (config.cache_dir / requested.repo.value / "os" / requested.arch.value / requested.database.value)).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")
		return FileResponse(static_file)
	else:
		raise HTTPException(status_code=404, detail="File not found")

@app.get("/{repo}/{arch}/{database}.tar.gz")
async def get_db_archive(repo :str, arch :str, database :str):
	requested = RepoArchive(repo=Repos[repo], arch=Architectures[arch], database=Archives[database])

	(config.cache_dir / requested.repo.value / "os" / requested.arch.value).mkdir(parents=True, exist_ok=True)

	if (static_file := (config.cache_dir / requested.arch.value / 'databases' / requested.repo.value / requested.database.value)).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")
		return FileResponse(static_file)
	else:
		raise HTTPException(status_code=404, detail="File not found")

@app.get("/{repo}/{arch}/{database}.db.sig")
async def get_db_signature(repo :str, arch :str, database :str):
	requested = RepoSignatures(repo=Repos[repo], arch=Architectures[arch], database=Signatures[database])

	(config.cache_dir / requested.repo.value / "os" / requested.arch.value).mkdir(parents=True, exist_ok=True)

	if (static_file := (config.cache_dir / requested.arch.value / 'databases' / requested.repo.value / requested.database.value)).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")

		return FileResponse(static_file)
	else:
		raise HTTPException(status_code=404, detail="File not found")

from collections import OrderedDict
def to_dict(d):
	result = {}
	for key, val in d.items():
		if isinstance(val, dict):
			val = to_dict(val)
		if isinstance(val, OrderedDict):
			val = to_dict(val)
		if isinstance(val, list):
			val = [to_dict(x) if isinstance(x, dict) else x for x in val]

		result[key] = val
	return result

@app.get("/{repo}/{arch}/{package}.pkg.tar.zst")
async def get_package(repo :str, arch :str, package :str):
	requested = Package(repo=Repos[repo], arch=Architectures[arch], package=package)

	(config.cache_dir / requested.repo.value / "os" / requested.arch.value).mkdir(parents=True, exist_ok=True)

	if (static_file := (config.cache_dir / requested.repo.value / "os" / requested.arch.value / f"{requested.package}.pkg.tar.zst")).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")

		return FileResponse(static_file)
	else:
		if not (torrent_file := (config.cache_dir / f"{requested.package}.pkg.tar.zst.torrent")).exists():
			# urllib.request.urlretrieve(f"https://hvornum.se/{requested.package}.pkg.tar.zst.torrent", str(torrent_file))
			raise ValueError(f"Missing torrent {torrent_file} - Ideally this would be downloaded from an upstream mirror, but for now you need to place it here manually.")
		
		torrent_session = libtorrent.session({'listen_interfaces': '0.0.0.0:6881'})
		with torrent_file.open('rb') as fh:
			torrent_info = to_dict(libtorrent.bdecode(fh.read()))

			content = torrent_session.add_torrent({
				'ti': libtorrent.torrent_info(torrent_info),
				'save_path': str(config.cache_dir)
			})

		status = content.status()
		
		_main = [thread for thread in threading.enumerate() if thread.name == 'MainThread'][0]
		while (not status.is_seeding) and _main.is_alive():
			status = content.status()

			print(f'{int(status.progress * 10000) / 100}% complete (down: {status.download_rate / 1000} kB/s up: {status.upload_rate / 1000} kB/s peers: {status.num_peers}) {status.state}')

			for alert in torrent_session.pop_alerts():
				if alert.category() & libtorrent.alert.category_t.error_notification:
					print(alert)

			sys.stdout.flush()
			await asyncio.sleep(1)

		print(f"Package from {content.status().name} downloaded")

@app.get("/{repo}/{arch}/{package}.pkg.tar.zst.sig")
async def get_package_signature(repo :str, arch :str, package :str):
	requested = Package(repo=Repos[repo], arch=Architectures[arch], package=package)

	(config.cache_dir / requested.repo.value / "os" / requested.arch.value).mkdir(parents=True, exist_ok=True)

	if (static_file := (config.cache_dir / requested.repo.value / "os" / requested.arch.value / f"{requested.package}.pkg.tar.zst.sig")).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")

		return FileResponse(static_file)
	else:
		if not (torrent_file := (config.cache_dir / f"{requested.package}.pkg.tar.zst.sig.torrent")).exists():
			# urllib.request.urlretrieve(f"https://hvornum.se/{requested.package}.pkg.tar.zst.sig.torrent", str(torrent_file))
			raise ValueError(f"Missing torrent {torrent_file} - Ideally this would be downloaded from an upstream mirror, but for now you need to place it here manually.")
		
		# https://libtorrent.org/python_binding.html
		torrent_session = libtorrent.session({'listen_interfaces': '0.0.0.0:6881'})
		with torrent_file.open('rb') as fh:
			# https://libtorrent.org/reference.html
			content = torrent_session.add_torrent({
				'ti': libtorrent.torrent_info(libtorrent.bdecode(fh.read())),
				'save_path': '.'
			})

		status = content.status()

		_main = [thread for thread in threading.enumerate() if thread.name == 'MainThread'][0]
		while (not status.is_seeding) and _main.is_alive() and session['terminating'] is False:
			status = content.status()

			print(f'{int(status.progress * 10000) / 100}% complete (down: {status.download_rate / 1000} kB/s up: {status.upload_rate / 1000} kB/s peers: {status.num_peers}) {status.state}')

			for alert in torrent_session.pop_alerts():
				if alert.category() & libtorrent.alert.category_t.error_notification:
					print(alert)

			time.sleep(1)

		print(f"Package from {content.status().name} downloaded")