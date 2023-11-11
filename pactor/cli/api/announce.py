from typing import Any
from fastapi import Request, Header, Response
from enum import Enum
from bencode import bdecode, bencode

from .main import app
from ...__init__ import __version__

class Event(Enum):
	started = 'started'
	stopped = 'stopped'
	completed = 'completed'
	keep_alive = 'keep_alive'

torrents = {
	
}

class bencodeResponse(Response):
	media_type = "text/plain"

	def render(self, content: Any) -> bytes:
		return content

def get_peers(info_hash, hide=None, requirecrypto=False):
	peer_list = []
	for peer in torrents[info_hash]['peers']:
		if hide and peer == hide:
			continue

		if requirecrypto and bool(torrents[info_hash]['peers']) == False:
			continue

		peer_id, port = peer.split(':')
		peer_list.append({
			"ip": torrents[info_hash]['peers'][peer]['ip'],
			"peer id": peer_id,
			"port": int(port)
		})
	return peer_list


@app.get("/announce", response_class=bencodeResponse)
def announcer(
	info_hash :str,
	peer_id :str,
	port :int,
	uploaded :int,
	downloaded :int,
	left :int,
	key :str,
	request: Request,
	event :Event = Event.keep_alive,
	compact :int = 0,
	redundant :int = 0,
	supportcrypto :int = 0,
	requirecrypto :int = 0,
	no_peer_id :int|None = None,
	numwant :int|None = None,
	corrupt :int|None = None,
	X_Real_IP: str|None = Header(None, include_in_schema=False)
):
	"""
	This is the /announce endpoint for the HTTP announce protocol defined in http://bittorrent.org/beps/bep_0052.html.
	Should be replaced by the proposed UDP tracker protocol http://bittorrent.org/beps/bep_0041.html in the future.

	The info_hash might appear twice as well in the future: http://bittorrent.org/beps/bep_0048.html

	:param info_hash: the hash identifying the torrent
	:type info_hash: str
	:param peer_id: a unique bytes string representing the client identity
	:type peer_id: str
	:param port: the port number that the client is listening on
	:type port: int
	:param uploaded: how many bytes the client has uploaded
	:type uploaded: int
	:param downloaded: how many bytes the client has downloaded
	:type downloaded: int
	:param left: how many chunks the client have left to download
	:type left: int
	:param key: undocumented
	:type key: str
	:param event: what client event triggered the announce (started, completed or stopped), default is Event.keep_alive
	:type event: Event, optional

	:param redundant: undocumented
	:type redundant: int, optional
	:param supportcrypto: indicates if the client supported crypto or not, defaults to 0
	:type supportcrypto: int, optional
	:param requirecrypto: indicates if the client requires crypto or not (as per discussion in https://forum.utorrent.com/topic/11398-crypto-tracker-extension/), defaults to 0
	:type requirecrypto: int, optional
	:param numwant: number of peers the client is requesting, defaults to 50
	:type numwant: int, optional
	:param compact: dictates if the returned peer-list should be in compact form or not (we force it off due to IPv6 until http://bittorrent.org/beps/bep_0007.html is accepted), defaults to 0 (off)
	:type compact: int, optional
	...
	:raises ValueError: If the given event is undefined
	...
	:return: bencodeResponse
	:rtype: bytes
	"""
	client_ip = request.client.host or X_Real_IP

	if not info_hash in torrents:
		torrents[info_hash] = {
			'peers' : {}
		}
	
	if event == Event.started:
	#if not f"{peer_id}:{port}" in torrents[info_hash]['peers']:
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
			'ip' : client_ip,
			'status' : event
		}
		peers = get_peers(info_hash, hide=f"{peer_id}:{port}", requirecrypto=requirecrypto)
	elif event == Event.completed:
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['downloaded'] = downloaded
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['uploaded'] = uploaded
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['status'] = event
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['corrupt'] = corrupt
		torrents[info_hash]['peers'][f"{peer_id}:{port}"]['left'] = left
		peers = get_peers(info_hash, hide=f"{peer_id}:{port}", requirecrypto=requirecrypto)
	elif event == Event.stopped:
		if torrents.get(info_hash, {}).get('peers', {}).get(f"{peer_id}:{port}"):
			del(torrents[info_hash]['peers'][f"{peer_id}:{port}"])
		peers = []
	elif event == Event.keep_alive:
		peers = []
	else:
		raise ValueError(f"Got unknown event: {event}")
	
	return bencodeResponse(
		bencode({
			"complete": 1,
			"incomplete": 0,
			"interval": 120,
			"min interval": 120,
			"peers": peers
		})
	)