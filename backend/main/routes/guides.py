import re
from pathlib import Path

from fastapi import HTTPException, APIRouter
from starlette.requests import Request
from starlette.responses import FileResponse, JSONResponse, RedirectResponse

from constants import CONTENT_PATH, GUIDES_PATH, exclude_guides, templates
from utils import find_file

router = APIRouter(prefix="/api/guides")

# Utils
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
    except Exception:
        pass
    return header

# Routes
@router.get("/")
async def guides(): return FileResponse(CONTENT_PATH / "guides/index.html")

@router.get("/{guide}/raw")
async def guides_raw(guide: str, request: Request):
    """Serve the raw guide template for a given guide name (with or without .md)."""
    guide_stem = guide
    if guide_stem.lower().endswith(".md"):
        guide_stem = guide_stem[:-3]
    # Case-insensitive search for the file
    found = None
    for f in GUIDES_PATH.glob("*.md"):
        if f.stem.lower() == guide_stem.lower():
            found = f
            break
    if not found or not found.is_file():
        raise HTTPException(status_code=404, detail="Guide not found")
    return templates.TemplateResponse(
        "raw_guide.html",
        {"request": request, "guide": f"/guides/{found.stem}.md"}
    )

@router.get("/list")
async def guides_list():
    """Return a JSON array of all guides (md files) in frontend/guides."""
    guides2 = []
    for md_file in GUIDES_PATH.glob("*.md"):
        if not md_file.name.strip() in exclude_guides:
            header = parse_guide_header(md_file)
            guides2.append({
                "name": md_file.name,
                "header": header
            })
    return JSONResponse(guides2)

@router.get("/list/{guide}")
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

@router.get("/{subpath:path}")
async def guides_handler(subpath: str, request: Request):
    """Handle guide requests with special processing for markdown files (except /raw and /list endpoints)."""

    file_path = find_file(f"guides/{subpath}")[0]
    # Handle files
    if (
        "." in subpath or
        (file_path and file_path.parent.is_dir() and file_path.parent.resolve() != (CONTENT_PATH / "guides").resolve())
    ):
        if not (file_path and file_path.is_file()):
            if subpath.endswith(".md"):
                return FileResponse(CONTENT_PATH / "guides" / "ERROR.md", status_code=404)
            else:
                raise HTTPException(status_code=404)
        else:
            return FileResponse(file_path)
    else:
        guide_name = f"{Path(subpath).stem.upper()}.md"
        if not (CONTENT_PATH / "guides" / guide_name).is_file():
            guide_name = "ERROR.md"
        # Preserve query parameters
        query_string = re.sub(r"&?guide=.*?(&|$)", "", request.url.query)
        redirect_url = f"/guides/?guide={guide_name}"
        if query_string:
            redirect_url += f"&{query_string}"
        return RedirectResponse(url=redirect_url)