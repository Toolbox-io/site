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
from bot import start_support_bot, stop_support_bot
import uvicorn

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting Toolbox.io server initialization...")


# noinspection PyUnusedLocal,PyShadowingNames
@asynccontextmanager
async def lifespan(app):
    """Lifespan event handler for FastAPI"""
    # Startup
    # Start support bot as background task
    bot_task = None
    if os.getenv("TELEGRAM_BOT_TOKEN"):
        logger.info("Starting support bot...")
        bot_task = asyncio.create_task(start_support_bot())

    yield

    # Shutdown
    if bot_task:
        logger.info("Stopping support bot...")
        await stop_support_bot()
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass


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

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
