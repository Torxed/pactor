import libtorrent
import os
import pathlib
import json
import logging
import datetime
import time
import hashlib
from typing import Callable
# from merkly.mtree import MerkleTree
from enum import Enum

from ...output import log

_V2_ONLY = 0b10000

def jsonify(obj):
	"""
	Converts objects into json.dumps() compatible nested dictionaries.
	Setting safe to True skips dictionary keys starting with a bang (!)
	"""

	compatible_types = str, int, float, bool, bytes
	if isinstance(obj, dict):
		return {
			jsonify(key): jsonify(value)
			for key, value in obj.items()
			if isinstance(key, compatible_types)
		}
	if isinstance(obj, Enum):
		return obj.value
	if isinstance(obj, bytes):
		return obj.decode('UTF-8', errors='replace')
	if hasattr(obj, 'json'):
		# json() is a friendly name for json-helper, it should return
		# a dictionary representation of the object so that it can be
		# processed by the json library.
		return jsonify(obj.json())
	if isinstance(obj, (datetime.datetime, datetime.date)):
		return obj.isoformat()
	if isinstance(obj, (list, set, tuple)):
		return [jsonify(item) for item in obj]
	if isinstance(obj, pathlib.Path):
		return str(obj)
	if hasattr(obj, "__dict__"):
		return vars(obj)

	return obj

class JSON(json.JSONEncoder, json.JSONDecoder):
	"""
	A safe JSON encoder that will omit private information in dicts (starting with !)
	"""

	def encode(self, obj) -> str:
		return super().encode(jsonify(obj))

def clean_metadata(dictionary):
	result = {}
	for key, val in dictionary.items():
		if key == "":
			continue

		if isinstance(val, dict):
			val = clean_metadata(val)

		result[key] = val
	return result

def calculate_pieces(file, piece_length=16384):
	# piece_size = 16384 # 16KiB

	with file.open('rb') as fh:
		data = fh.read()
	
	pieces = [hashlib.sha1(data[i:i+piece_length]).digest() for i in range(0, len(data), piece_length)]
	return pieces

def calculate_layers(file):
	return b''

def sha256(part1, part2=None):
	return hashlib.sha256(part1.encode()).hexdigest()

# 
# 
def torrent(args, **kwargs):
	"""
	Creates a V! torrent file.
	TODO: Once rtorrent, deluge or tranmission (or any other popular client)
	      starts supporting V2 torrents, we should move over immediately!
	      It has a nice way of hashign pieces and enabling better verification.
	      (which could allow us to do a .torrent of a whole repo structure)

	 * http://bittorrent.org/beps/bep_0052.html
	 * https://blog.libtorrent.org/2020/09/bittorrent-v2/
	 * https://en.wikipedia.org/wiki/Torrent_file#BitTorrent_v2
	 * https://medium.com/@alexandre.laplante/a-simple-explanation-of-merkle-trees-5bd90191d3b9
	 * https://pypi.org/project/merkly/
	 * https://github.com/arvidn/libtorrent/issues/6395
	 * https://stackoverflow.com/questions/74073079/bittorrent-why-use-merkle-tree-for-data-integrity
	 * http://bittorrent.org/beps/bep_0030.html
	 * https://docs.picotorrent.org/en/master/creating-torrents.html
	"""

	# We need to create a relative path to populate the "path" key in the file(s).
	paths = []
	_prev = None
	for _path in list(reversed(list((args.file.relative_to(args.workdir)).parents)))[1:]:
		path = _path

		if _prev:
			path = path.relative_to(_prev)

		paths.append(path)

		_prev = _path

	torrent = {
		b'announce': args.announce.encode(),
		b'created by': args.created_by.encode(),
		b'creation date': int(time.time()),
		b'info': {
			b'files': [
				{
					b'length': os.stat(args.file).st_size,
					b'path': [*[str(path) for path in paths[1:]], str(args.file.name)]
				}
			],
			b'name': str(paths[0]).encode(),
			b'piece length': 16384,
			b'pieces': b''.join(calculate_pieces(args.file, piece_length=16384))
		}
	}

	torrent_file = libtorrent.bencode(torrent)
	with args.outfile.open('wb') as fh:
		fh.write(torrent_file)