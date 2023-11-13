import pathlib
import tomllib
import os

from .models import Configuration

config_location = None
if (path := pathlib.Path('./pactor.toml')).exists():
	config_location = path
elif (path := pathlib.Path(f"{os.environ.get('CONFDIR', '/etc/pactor')}/pactor.toml")).exists():
	config_location = path

if not config_location:
	#raise KeyError("Need a pactor.toml configuration file")
	config = None
else:
	with config_location.open('rb') as f:
		config = Configuration(**tomllib.load(f))