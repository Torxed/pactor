import logging
import uvicorn
from fastapi import FastAPI

from ...output import log

app = FastAPI()

def main(args, **kwargs):
	# args.addr
	from .version import version
	from .db import get_db
	from .announce import announcer

	log(f"Started up pactor's API entrypoint", level=logging.INFO, fg="green")
	uvicorn.run(app, host=args.addr, port=args.port)

def announce(args, **kwargs):
	# args.addr
	from .version import version
	from .announce import announcer

	log(f"Started up pactor's API entrypoint", level=logging.INFO, fg="green")
	uvicorn.run(app, host=args.addr, port=args.port)
