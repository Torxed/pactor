import pathlib
from ..args import subparsers
from ..api.main import main as parse_api_main

parse_pactor = subparsers.add_parser("api", help="Starts the mock Arch Linux mirror locally")
parse_pactor.add_argument(
	"--addr",
	required=False,
	type=str,
	default='127.0.0.1',
	help="Which destinations do this server have?",
)
parse_pactor.add_argument(
	"--port",
	required=False,
	type=int,
	default=8001,
	help="Which port do this server listen to?",
)
parse_pactor.set_defaults(func=parse_api_main)
