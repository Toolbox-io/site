from starlette.responses import FileResponse

from constants import CONTENT_PATH
from app import app


@app.get("/")
async def index(): return FileResponse(CONTENT_PATH / "index.html")

@app.get("/favicon.ico")
async def favicon(): return FileResponse(CONTENT_PATH / "res" / "favicon.svg")