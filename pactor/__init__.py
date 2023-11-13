import signal
import sys
from .cli.args_router import loaded
from .cli.args import load_arguments
from .config import config, Configuration

__version__ = "0.1"

def signal_handler(sig, frame):
	from .session import session
	session['terminating'] = True
	sys.exit(0)

def run_as_a_module():
	args = load_arguments()

	if config:
		for key, val in args._get_kwargs():
			if key in Configuration.__fields__:
				setattr(config, key, val)

	#config.cache_dir = args

	signal.signal(signal.SIGINT, signal_handler)

	args.func(args)
