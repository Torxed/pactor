import logging
import uvicorn
from fastapi import FastAPI

from ...output import log
from ...session import session, config
from ...database.postgresql import Database

app = FastAPI()

def main(args, **kwargs):
	# args.addr
	from .version import version
	from .mirror import get_db

	log(f"Started up pactor's mirror entrypoint", level=logging.INFO, fg="green")
	uvicorn.run(app, host=args.addr, port=args.port)

def announce(args, **kwargs):
	from .version import version
	from .announce import announcer

	log(f"Started up pactor's announce entrypoint", level=logging.INFO, fg="green")
	uvicorn.run(app, host=args.addr, port=args.port)
