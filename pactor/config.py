import pathlib
import os

from .models import Configuration

config_location = None
if (path := pathlib.Path('./pactor.toml')).exists():
	config_location = path
elif (path := pathlib.Path(f"{os.environ.get('CONFDIR', '/etc/pactor')}/pactor.toml")).exists():
	config_location = path

if not config_location:
	raise KeyError("Need a pactor.toml configuration file")

try:
	# Py3.10+
	import tomllib
	file_mode = 'rb'
except:
	# Py3.9 or below (external dep needed)
	import toml as tomllib
	file_mode = 'r'

with config_location.open(file_mode) as f:
	config = Configuration(**tomllib.load(f))