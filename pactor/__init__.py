from .cli.args_router import loaded
from .cli.args import load_arguments

__version__ = "0.1"

def run_as_a_module():
	args = load_arguments()
	args.func(args)
