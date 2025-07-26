from _typeshed import FileDescriptorOrPath
import os
from functools import wraps
from pathlib import Path
from typing import Tuple, Optional

from fastapi import APIRouter, HTTPException, UploadFile
from starlette.staticfiles import StaticFiles

from constants import CONTENT_PATH

router = APIRouter()

def find_file(path: str) -> Tuple[Optional[Path], Optional[str]]:
    """
    Find a file with the given path, handling various cases like directories and extensions.
    Returns a tuple of (file_path, redirect_path).
    Only matches files whose relative path matches the request path.
    """
    # Normalize the path
    norm_path = Path(path)
    full_path = CONTENT_PATH / norm_path

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
            # Only match if the request path matches the relative path
            rel = dir_html.relative_to(CONTENT_PATH).with_suffix("").as_posix()
            if rel == path:
                return dir_html, None
        return None, None

    # Handle file without extension
    if full_path.is_file():
        return full_path, None

    # Handle .html extension
    html_path = CONTENT_PATH / f"{norm_path}.html"
    if html_path.is_file():
        rel = html_path.relative_to(CONTENT_PATH).with_suffix("").as_posix()
        if rel == path:
            return html_path, None

    # Do NOT search in subdirectories by filename only (remove rglob fallback)
    return None, None


def static(path: str | Path):
    if not isinstance(path, Path):
        path = Path(path)
    path = str(path.resolve())

    router.mount(path, StaticFiles(directory=path), name=path)

def debug_only(route_handler):
    @wraps(route_handler)
    async def wrapper(*args, **kwargs):
        debug = os.getenv("DEBUG", "false").lower() == "true"
        if not debug:
            # Pass to next handler by raising 404 (FastAPI will continue searching)
            raise HTTPException(status_code=404)
        return await route_handler(*args, **kwargs)
    return wrapper

def trim_margin(text: str, margin: str = '|') -> str:
    """
    Removes leading whitespace and the margin prefix from each line in the input string.
    :param text: The multiline string to process.
    :param margin: The margin prefix to trim (default is '|').
    :return: The processed string with margins trimmed.
    """
    lines = text.splitlines()
    trimmed_lines = []
    for line in lines:
        # Find the margin prefix in the line after leading whitespace
        stripped = line.lstrip()
        if stripped.startswith(margin):
            # Remove up to and including the margin prefix
            idx = line.index(margin)
            trimmed_lines.append(line[idx + len(margin):])
        else:
            trimmed_lines.append(line)
    return '\n'.join(trimmed_lines)

class FileTooLargeError(Exception): pass

async def save_file(input: UploadFile, output: FileDescriptorOrPath, max_size: int = 0, chunk_size: int = 1024 * 1024):
    total_size = 0
    with open(output, "wb") as out_file:
        while True:
            chunk = await input.read(chunk_size)
            if not chunk:
                break
            total_size += len(chunk)
            if max_size != 0 and total_size > max_size:
                out_file.close()
                os.remove(output)
                raise FileTooLargeError()
            out_file.write(chunk)
    
    return total_size