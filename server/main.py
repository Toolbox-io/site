import mimetypes

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse

from app import app
from constants import *
from utils import find_file

# Import routes after app is defined
# noinspection PyUnresolvedReferences
import routes.core
# noinspection PyUnresolvedReferences
import routes.guides

@app.get("/{path:path}")
async def serve_files(path: str, request: Request):
    """Serve .mdpage.md files first, then files from the content directory with various fallbacks."""
    # 1. Try to serve .mdpage.md file first
    if (CONTENT_PATH / f"{path}.page.md").is_file():
        return templates.TemplateResponse(
            "mdpage.html",
            {"request": request, "file": f"{path}.page.md"}
        )

    # 2. Fallback to regular file logic
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
    import os

    port = 80  # Default port
    config_path = os.path.join(os.path.dirname(__file__), 'server.properties')
    if os.path.isfile(config_path):
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("port="):
                    try:
                        port = int(line.split("=", 1)[1])
                    except ValueError:
                        pass
                    break
    uvicorn.run(app, host="0.0.0.0", port=port)
