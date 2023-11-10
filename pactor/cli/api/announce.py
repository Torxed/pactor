from typing import Any
from fastapi import Request, Header, Response
from enum import Enum
from bencode import bdecode, bencode

from .main import app
from ...__init__ import __version__

class Event(Enum):
	started = 'started'

torrents = {
	
}

class bencodeResponse(Response):
	media_type = "text/plain"

	def render(self, content: Any) -> bytes:
		return content

@app.get("/announce", response_class=bencodeResponse)
def announcer(
	info_hash :str,
	peer_id :str,
	port :int,
	uploaded :float,
	downloaded :float,
	left :float,
	key :str,
	event :Event,
	compact :int,
	request: Request,
	redundant :int = 0,
	supportcrypto :int = 0,
	no_peer_id :int|None = None,
	numwant :float|None = None,
	corrupt :float|None = None,
	X_Real_IP: str|None = Header(None, include_in_schema=False)
):
	"""
	:info_hash = info_hash=%91%f8%c1%5b%c7)%0cJ%26%85%09%a3%99%b4%16%3eP!%8e%24
	:peer_id = -DE211s-Zcz8jz)oBJBa
	:port = 65281
	:uploaded = 0
	:downloaded = 0
	:left = 0
	:corrupt = 0
	:key = 2DA51493
	:event = started
	:numwant = 200
	:compact = 1
	:no_peer_id = 1
	:supportcrypto = 1
	:redundant = 0
	"""
	client_ip = request.client.host or X_Real_IP

	if not info_hash in torrents:
		torrents[info_hash] = {
			'peers' : {}
		}
	
	if not f"{peer_id}:{port}" in torrents[info_hash]['peers']:
		torrents[info_hash]['peers'][f"{peer_id}:{port}"] = {
			'downloaded' : downloaded,
			'uploaded' : uploaded,
			'corrupt' : corrupt,
			'left' : left,
			'supportcrypto' : supportcrypto,
			'no_peer_id' : no_peer_id,
			'port' : port,
			'numwant' : numwant,
			'key' : key,
			'status' : event
		}
	else:
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['downloaded'] = downloaded
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['uploaded'] = uploaded
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['status'] = event
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['corrupt'] = corrupt
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['left'] = left
	
	return bencodeResponse(bencode({'complete': 1, 'downloaded': 0, 'incomplete': 0, 'interval': 1969, 'min interval': 984, 'peers': b'\n\n\x00\x01\xff\x01'}))
	# print(client_ip, [info_hash, peer_id, port, uploaded, downloaded, left, corrupt, key, event, numwant, compact, no_peer_id, supportcrypto, redundant])