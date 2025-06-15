import mimetypes
import re
from pathlib import Path
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles

app = FastAPI()

# Constants
CONTENT_PATH = Path("src")
TEMPLATES_PATH = CONTENT_PATH / "templates"
GUIDES_PATH = CONTENT_PATH / "guides"
exclude_guides = ["README.md", "ERROR.md"]

# Setup templates
templates = Jinja2Templates(directory=str(TEMPLATES_PATH))

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

def parse_guide_header(md_path: Path) -> dict:
    """Parse the header from a markdown file. Header is expected as a YAML-like block at the top."""
    header = {}
    try:
        with md_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()
        if lines and lines[0].strip() == "---":
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                if ":" in line:
                    k, v = line.split(":", 1)
                    header[k.strip()] = v.strip().strip('"')
    except Exception: pass
    return header

@app.get("/guides/{guide}/raw")
async def guides_raw(guide: str, request: Request):
    """Serve the raw guide template for a given guide name (with or without .md)."""
    if not guide.lower().endswith(".md"):
        guide += ".md"
    md_path = GUIDES_PATH / guide
    if not md_path.is_file():
        raise HTTPException(status_code=404, detail="Guide not found")
    return templates.TemplateResponse(
        "raw_guide.html",
        {"request": request, "guide": f"guides/{Path(guide).stem}.md"}
    )

@app.get("/guides/list")
async def guides_list():
    """Return a JSON array of all guides (md files) in src/guides."""
    guides2 = []
    for md_file in GUIDES_PATH.glob("*.md"):
        if not md_file.name.strip() in exclude_guides:
            header = parse_guide_header(md_file)
            guides2.append({
                "name": md_file.name,
                "header": header
            })
    return JSONResponse(guides2)

@app.get("/guides/list/{guide}")
async def guide_info(guide: str):
    """Return JSON info for a single guide (with or without .md)."""
    if not guide.lower().endswith(".md"):
        guide += ".md"
    if not f"{guide.replace(".md", "").upper()}.md" in exclude_guides:
        md_path = GUIDES_PATH / guide
        if not md_path.is_file():
            raise HTTPException(status_code=404, detail="Guide not found")
        header = parse_guide_header(md_path)
        return JSONResponse({
            "name": md_path.name,
            "header": header
        })
    else:
        raise HTTPException(status_code=404, detail="Guide not found")

@app.get("/guides/{subpath:path}")
async def guides_handler(subpath: str, request: Request):
    """Handle guide requests with special processing for markdown files (except /raw and /list endpoints)."""

    file_path, redirect_path = find_file(f"guides/{subpath}")
    # Handle files
    if (
        "." in subpath or
        (file_path and file_path.parent.is_dir() and file_path.parent.resolve() != (CONTENT_PATH / "guides").resolve())
    ):
        if not (file_path and file_path.is_file()):
            if subpath.endswith(".md"):
                return FileResponse((CONTENT_PATH / "guides" / "ERROR.md").resolve(), status_code=404)
            raise HTTPException(status_code=404)
        return FileResponse(file_path)
    # Redirect for not found guides
    guide_name = f"{Path(subpath).stem.upper()}.md"
    if not (CONTENT_PATH / "guides" / guide_name).is_file():
        guide_name = "ERROR.md"
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
