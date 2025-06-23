from fastapi import APIRouter
from starlette.responses import FileResponse

from constants import CONTENT_PATH

router = APIRouter()

@router.get("/")
async def index(): return FileResponse(CONTENT_PATH / "index.html")

@router.get("/favicon.ico")
async def favicon(): return FileResponse(CONTENT_PATH / "res" / "favicon.svg")