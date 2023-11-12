import signal
import sys
from .cli.args_router import loaded
from .cli.args import load_arguments

__version__ = "0.1"

def signal_handler(sig, frame):
	from .session import session
	session['terminating'] = True
	sys.exit(0)

def run_as_a_module():
	args = load_arguments()

	signal.signal(signal.SIGINT, signal_handler)

	args.func(args)
