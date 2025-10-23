import asyncio
import logging
import sys
import os
from contextlib import asynccontextmanager
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

# Load .env file from project root (two levels up from backend/main)
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

from fastapi import Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import app
from constants import *
from db.init import initialize_database
import uvicorn

# Configure logging
logger = logging.getLogger(__name__)


# noinspection PyUnusedLocal,PyShadowingNames
@asynccontextmanager
async def lifespan(app):
    """Lifespan event handler for FastAPI"""
    # Startup
    yield

    # Shutdown


# Update the app with lifespan
app.router.lifespan_context = lifespan




@app.exception_handler(StarletteHTTPException)
async def http_exception(request: Request, exc: StarletteHTTPException):
    if request.headers.get("content-type") == "application/json":
        return await http_exception_handler(request, exc)

    path = CONTENT_PATH / "error" / f"{exc.status_code}.html"
    if path and path.exists():
        return FileResponse(path=path, status_code=exc.status_code)
    if exc.status_code in [401, 403]:
        return FileResponse(path=CONTENT_PATH / "error" / "401or403.html", status_code=exc.status_code)

    return await http_exception_handler(request, exc)


if __name__ == "__main__":
    # Initialize database before starting the server
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        sys.exit(1)
