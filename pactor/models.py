from pydantic import BaseModel


class DBConfig(BaseModel):
	password :str|None = None
	hostname :str = '127.0.01'
	username :str = 'coreborn'
	database :str = 'coreborn'
	

class Configuration(BaseModel):
	db :DBConfig
