import argparse
import pathlib
# https://towardsdatascience.com/dynamically-add-arguments-to-argparse-python-patterns-a439121abc39

parser = argparse.ArgumentParser("spfcheck")
parser.add_argument(
	"--cache-dir",
	required=False,
	type=pathlib.Path,
	default=pathlib.Path('/var/cache/pactor/'),
	help="Where to store ",
)
subparsers = parser.add_subparsers(help="Sub-commands help")

def load_arguments():
	from ..session import session

	session['args'] = parser.parse_args()

	return session['args']
