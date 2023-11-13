import os
import pathlib
from pydantic import BaseModel


class DBConfig(BaseModel):
	hostname :str = '127.0.01'
	username :str = 'pactor'
	password :str = 'pactor'
	database :str = 'pactor'
	

class Configuration(BaseModel):
	db :DBConfig
	addr :str = os.environ.get('addr', '127.0.0.1')
	port :int = int(os.environ.get('addr', 8001))
	cache_dir :pathlib.Path = pathlib.Path(os.environ.get('cache-dir', '/var/cache/pactor/'))
