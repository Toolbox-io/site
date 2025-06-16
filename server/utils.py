from pathlib import Path
from typing import Tuple, Optional

from starlette.staticfiles import StaticFiles

from constants import CONTENT_PATH
from app import app


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