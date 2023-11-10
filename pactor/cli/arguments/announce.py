import pathlib
from ..args import subparsers
from ..api.main import announce

parse_announce = subparsers.add_parser("announce", help="Starts the mock Arch Linux mirror locally")
parse_announce.add_argument(
	"--addr",
	required=False,
	type=str,
	default='127.0.0.1',
	help="Which destinations do this server have?",
)
parse_announce.add_argument(
	"--port",
	required=False,
	type=int,
	default=8002,
	help="Which port do this server listen to?",
)
parse_announce.set_defaults(func=announce)
