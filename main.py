import mimetypes
import re
from pathlib import Path
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

app = FastAPI()

# Constants
CONTENT_PATH = Path("src")
TEMPLATES_PATH = CONTENT_PATH / "templates"
LOGFILE = "server.log"

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_PATH))

# Init log
with open(LOGFILE, "w") as _log:
    _log.write("Starting server...")

def write_log(msg: str):
    print(msg)
    with open(LOGFILE, "a") as log:
        log.write(msg + "\n")


def find_file(path: str) -> Tuple[Optional[Path], Optional[str]]:
    """
    Find a file with the given path, handling various cases like directories and extensions.
    Returns a tuple of (file_path, redirect_path).
    """
    full_path = CONTENT_PATH / path

    # Handle directory case
    if full_path.is_dir():
        index_file = full_path / "index.html"
        if index_file.is_file():
            if not path.endswith("/"):
                return index_file, f"{path}/"
            return index_file, None
        
        # Check for <dir>.html in parent directory
        dir_html = full_path.parent / f"{full_path.name}.html"
        if dir_html.is_file():
            return dir_html, None
        return None, None

    # Handle file without extension
    if full_path.is_file():
        return full_path, None

    # Handle .html extension
    html_path = CONTENT_PATH / f"{path}.html"
    if html_path.is_file():
        return html_path, None

    # Search in subdirectories
    for file_path in CONTENT_PATH.rglob("*"):
        if file_path.is_file() and file_path.name.startswith(path):
            return file_path, None

    return None, None

def static(path: str | Path):
    if not path is Path:
        path = Path(path)
    path = str(path.resolve())

    app.mount(path, StaticFiles(directory=path), name=path)

@app.get("/")
async def index(): return FileResponse(CONTENT_PATH / "index.html")

@app.get("/favicon.ico")
async def favicon(): return FileResponse(CONTENT_PATH / "res" / "favicon.svg")

@app.get("/guides/")
async def guides(): return FileResponse(CONTENT_PATH / "guides/index.html")

@app.get("/guides/{subpath:path}")
async def guides_handler(subpath: str, request: Request):
    """Handle guide requests with special processing for markdown files."""

    file_path, redirect_path = find_file(f"guides/{subpath}")
    
    # Handle files
    if (
        "." in subpath or
        (file_path and file_path.parent.is_dir() and file_path.parent.resolve() != (CONTENT_PATH / "guides").resolve())
    ):
        if not (file_path and file_path.is_file()):
            raise HTTPException(status_code=404)
        return FileResponse(file_path)
    
    # Handle /raw endpoint
    if subpath.lower().endswith('/raw'):
        return templates.TemplateResponse(
            "raw_guide.html",
            {"request": request, "guide": f"guides/{Path(subpath).parent.name}.md"}
        )
    
    # Redirect for not found guides
    guide_name = f"{Path(subpath).stem.upper()}.md"

    if not (CONTENT_PATH / "guides" / guide_name).is_file():
        raise HTTPException(
            status_code=404,
            detail=f"""
            # Ошибка
            Извините, гайд {guide_name} не был найден на сервере.
            
            [Все гайды](/guides)
            """
        )

    # Preserve query parameters
    query_string = re.sub(r"&?guide=.*?(&|$)", "", request.url.query)
    redirect_url = f"/guides/?guide={guide_name}"
    if query_string:
        redirect_url += f"&{query_string}"
    return RedirectResponse(url=redirect_url)

@app.get("/{path:path}")
async def serve_files(path: str, request: Request):
    """Serve files from the content directory with various fallbacks."""
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
        return RedirectResponse(url=redirect_url)
    
    if not file_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    mime_type, _ = mimetypes.guess_type(str(file_path))
    return FileResponse(
        path=file_path,
        media_type=mime_type
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
