import logging
import uvicorn
from fastapi import FastAPI

from ...output import log

app = FastAPI()

def main(args, **kwargs):
	# args.addr
	from .version import version
	from .db import get_db

	log(f"Started up pactor's mirror entrypoint", level=logging.INFO, fg="green")
	uvicorn.run('pactor.cli.api.db:app', host=args.addr, port=args.port, workers=5)

def announce(args, **kwargs):
	# args.addr
	from .version import version
	from .announce import announcer

	log(f"Started up pactor's announce entrypoint", level=logging.INFO, fg="green")
	uvicorn.run('pactor.cli.api.announce:app', host=args.addr, port=args.port, workers=5)
