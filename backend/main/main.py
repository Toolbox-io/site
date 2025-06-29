import logging
import mimetypes
import sys

from fastapi import HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import FileResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import app
from constants import *
from db_init import initialize_database
from utils import find_file

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Starting Toolbox.io server initialization...")

@app.get("/{path:path}")
async def serve_files(path: str, request: Request):
    """Serve .mdpage.md files first, then files from the content directory with various fallbacks."""
    mdpath = path.upper()
    
    # Log request for monitoring
    logger.info(f"Serving request: {request.method} {request.url.path} from {request.client.host}")
    
    # 1. Try to serve .mdpage.md file first
    if (CONTENT_PATH / f"{mdpath}.page.md").resolve().is_file():
        logger.info(f"Serving markdown page: {mdpath}.page.md")
        return templates.TemplateResponse(
            "mdpage.html",
            {"request": request, "file": f"{mdpath}.page.md"}
        )

    # 2. Fallback to regular file logic
    logger.debug(f"Looking up file for path: {path}")
    file_path, redirect_path = find_file(path)
    
    if redirect_path:
        # Preserve query parameters
        query_string = request.url.query
        redirect_url = redirect_path
        if query_string:
            if '?' in redirect_url:
                redirect_url += f"&{query_string}"
            else:
                redirect_url += f"?{query_string}"
        logger.info(f"Redirecting to: {redirect_url}")
        return RedirectResponse(url=redirect_url)
    
    if not file_path:
        logger.warning(f"File not found: {path}")
        raise HTTPException(status_code=404, detail="File not found")

    if (
        file_path.name.endswith(".ts") or
        file_path.name.endswith(".scss") or
        file_path.name.endswith(".sh") or
        file_path.name == "package.json" or
        file_path.name == "tsconfig.json" or
        file_path.parent.resolve() == (CONTENT_PATH / "templates").resolve() or
        file_path.parent.resolve() == (CONTENT_PATH / "emails").resolve()
    ):
        logger.warning(f"Access denied to: {file_path}")
        raise HTTPException(status_code=404, detail="Access denied")
    
    mime_type, _ = mimetypes.guess_type(str(file_path))
    logger.info(f"Serving file: {file_path} (type: {mime_type})")
    return FileResponse(
        path=file_path,
        media_type=mime_type
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception(request: Request, exc: StarletteHTTPException):
    path = CONTENT_PATH / "error" / f"{exc.status_code}.html"
    if path and path.exists():
        return FileResponse(path=path, status_code=exc.status_code)
    if exc.status_code in [401, 403]:
        return FileResponse(path=CONTENT_PATH / "error" / "401or403.html", status_code=exc.status_code)

    return await http_exception_handler(request, exc)

if __name__ == "__main__":
    import uvicorn
    # Initialize database before starting the server
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        sys.exit(1)
    logger.info("Starting Toolbox.io server...")
    logger.info(f"Server will run on host: 0.0.0.0, port: 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
