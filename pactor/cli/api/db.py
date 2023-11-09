import pydantic
import os
from enum import Enum
from fastapi import HTTPException
from fastapi.responses import FileResponse

from .main import app
from ...session import session
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

	if (static_file := (session['args'].cache_dir / requested.arch.value / 'databases' / requested.repo.value / requested.database.value)).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")
		return FileResponse(static_file)
	else:
		raise HTTPException(status_code=404, detail="File not found")

@app.get("/{repo}/{arch}/{database}.tar.gz")
async def get_db(repo :str, arch :str, database :str):
	requested = RepoArchive(repo=Repos[repo], arch=Architectures[arch], database=Archives[database])

	if (static_file := (session['args'].cache_dir / requested.arch.value / 'databases' / requested.repo.value / requested.database.value)).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")
		return FileResponse(static_file)
	else:
		raise HTTPException(status_code=404, detail="File not found")

@app.get("/{repo}/{arch}/{database}.db.sig")
async def get_db(repo :str, arch :str, database :str):
	requested = RepoSignatures(repo=Repos[repo], arch=Architectures[arch], database=Signatures[database])

	if (static_file := (session['args'].cache_dir / requested.arch.value / 'databases' / requested.repo.value / requested.database.value)).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")

		return FileResponse(static_file)
	else:
		raise HTTPException(status_code=404, detail="File not found")

@app.get("/{repo}/{arch}/{package}.pkg.tar.zst")
async def get_db(repo :str, arch :str, package :str):
	requested = Package(repo=Repos[repo], arch=Architectures[arch], package=package)

	if (static_file := (session['args'].cache_dir / requested.arch.value / 'packages' / requested.repo.value / f"{requested.package}.pkg.tar.zst")).exists():
		if os.stat(str(static_file)).st_size == 0:
			raise HTTPException(status_code=404, detail="File not found")

		return FileResponse(static_file)
	else:
		return TorrentThis(requested)