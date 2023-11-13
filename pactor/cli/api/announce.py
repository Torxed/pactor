import logging
import uvicorn
import libtorrent
import base64
from typing import Any
from fastapi import Request, Header, Response
from enum import Enum
from fastapi import FastAPI

from .main import app
from ...__init__ import __version__
from ...session import session, config
from ...database.postgresql import Database

session['db'] = Database(dbname=config.db.database, user=config.db.username, password=config.db.password, host=config.db.hostname)
session['db'].init()

class Event(Enum):
	started = 'started'
	stopped = 'stopped'
	completed = 'completed'
	keep_alive = 'keep_alive'


class bencodeResponse(Response):
	media_type = "text/plain"

	def render(self, content: Any) -> bytes:
		return content

def get_peers(info_hash, hide=None, requirecrypto=False):
	peer_list = []
	for peer in session['db'].query("SELECT * FROM announcements WHERE info_hash=%s AND peer_id != %s AND peer_port != %s AND event != 'stopped' AND requirecrypto=%s", (
		base64.b64encode(info_hash.encode('UTF-8')).decode(),
		base64.b64encode(hide[0].encode('UTF-8')).decode(),
		hide[1],
		str(requirecrypto)[0].lower()
	), force_list=True):

		peer_list.append({
			"ip": peer['peer_ip'],
			"peer id": peer['peer_id'],
			"port": int(peer['peer_port'])
		})

	print(f"Found peers: {peer_list}")
	return peer_list

@app.get("/version")
def version():
	return {"version": __version__}

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
	client_ip = X_Real_IP or request.client.host
	
	if event == Event.started:
		session['db'].query("INSERT INTO announcements (info_hash, peer_id, peer_ip, peer_port, event) VALUES (%s, %s, %s, %s, %s)", (base64.b64encode(info_hash.encode()).decode(), base64.b64encode(peer_id.encode('UTF-8')).decode(), client_ip, port, event.value))

		peers = get_peers(info_hash, hide=(peer_id, port), requirecrypto=bool(requirecrypto))
	elif event == Event.completed:
		session['db'].query("UPDATE announcements SET downloaded=%s, uploaded=%s, event=%s, pieces_left=%s WHERE info_hash=%s AND peer_id=%s AND peer_port=%s", (
			downloaded, uploaded, event.value, left, base64.b64encode(info_hash.encode()).decode(), base64.b64encode(peer_id.encode('UTF-8')).decode(), port
		))

		peers = get_peers(info_hash, hide=(peer_id, port), requirecrypto=bool(requirecrypto))
	elif event == Event.stopped:
		session['db'].query("UPDATE announcements SET downloaded=%s, uploaded=%s, event=%s, pieces_left=%s WHERE info_hash=%s AND peer_id=%s AND peer_port=%s", (
			downloaded, uploaded, event.value, left, base64.b64encode(info_hash.encode()).decode(), base64.b64encode(peer_id.encode('UTF-8')).decode(), port
		))

		peers = []
	elif event == Event.keep_alive:
		peers = []
	else:
		raise ValueError(f"Got unknown event: {event}")
	
	return bencodeResponse(
		libtorrent.bencode({
			"complete": 1,
			"incomplete": 0,
			"interval": 120,
			"min interval": 120,
			"peers": peers
		})
	)