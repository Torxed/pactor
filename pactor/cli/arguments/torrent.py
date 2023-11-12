import pathlib
from ..args import subparsers
from ..torrent.main import torrent

parse_torrent = subparsers.add_parser("torrent", help="Starts the mock Arch Linux mirror locally")
parse_torrent.add_argument(
	"--file",
	required=True,
	type=pathlib.Path,
	help="Path to a file to put into the torrent",
)
parse_torrent.add_argument(
	"--workdir",
	required=False,
	type=pathlib.Path,
	help="When creating file tree and hashes, which folder to relate from",
)
parse_torrent.add_argument(
	"--comment",
	required=False,
	type=str,
	default="Arch Linux Package",
	help="What comment to add into the torrent",
)
parse_torrent.add_argument(
	"--created-by",
	required=False,
	type=str,
	default="Arch Linux",
	help="Who's the creator?",
)
parse_torrent.add_argument(
	"--announce",
	required=False,
	type=str,
	default="http://announce.archlinux.life:8002/announce",
	help="Which port do this server listen to?",
)
parse_torrent.add_argument(
	"--outfile",
	required=True,
	type=pathlib.Path,
	help="What filename to save the torrent to",
)

parse_torrent.set_defaults(func=torrent)
