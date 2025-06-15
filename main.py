import mimetypes
from pathlib import Path
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# Constants
CONTENT_PATH = Path("src")
TEMPLATES_PATH = CONTENT_PATH / "templates"

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

@app.get("/")
async def index():
    """Serve the index.html file from the content directory."""
    index_path = CONTENT_PATH / "index.html"
    if not index_path.is_file():
        raise HTTPException(status_code=404, detail="Index file not found")
    return FileResponse(index_path)

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

@app.get("/guides/{subpath:path}")
async def guides_handler(subpath: str, request: Request):
    """Handle guide requests with special processing for markdown files."""

    print("guide handler called")

    file_path, redirect_path = find_file(f"guides/{subpath}")
    
    # Handle raw markdown files
    if file_path and ((subpath.lower().endswith('.md') and file_path.suffix == '.md') or "." in subpath):
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return FileResponse(
            path=file_path,
            media_type=mime_type
        )
    
    # Handle markdown files for processing
    if not subpath.lower().endswith('.md') and file_path and file_path.suffix == '.md':
        guide_name = file_path.stem
        return HTMLResponse(content=f"""
        <html>
        <head><title>Guide: {guide_name}</title></head>
        <body>
            <h1>Processed Guide: {guide_name}</h1>
            <p>This is a processed guide for: <b>{guide_name}</b></p>
        </body>
        </html>
        """)
    
    # Handle /raw endpoint
    if subpath.lower().endswith('/raw'):
        return templates.TemplateResponse(
            "raw_guide.html",
            {"request": request, "guide": f"GUIDES/{Path(subpath).parent.name.upper()}.MD"}
        )
    
    # Redirect for not found guides
    guide_name = f"{Path(subpath).stem.upper()}.md"
    # Preserve query parameters
    query_string = request.url.query
    redirect_url = f"/guides?guide={guide_name}"
    if query_string:
        if '?' in redirect_url:
            redirect_url += f"&{query_string}"
        else:
            redirect_url += f"?{query_string}"
    return RedirectResponse(url=redirect_url)

@app.get("/favicon.ico")
async def favicon():
    """Serve the favicon."""

    print("returning favicon")

    favicon_path = CONTENT_PATH / "res" / "favicon.svg"
    if not favicon_path.is_file():
        raise HTTPException(status_code=404, detail="Favicon not found")
    
    mime_type, _ = mimetypes.guess_type(str(favicon_path))
    return FileResponse(
        path=favicon_path,
        media_type=mime_type
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
