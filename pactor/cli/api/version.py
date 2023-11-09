from .main import app
from ...__init__ import __version__

@app.get("/version")
def version():
	return {"version": __version__}