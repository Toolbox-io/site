# Constants
from pathlib import Path

from starlette.templating import Jinja2Templates

CONTENT_PATH = Path("../../frontend")
TEMPLATES_PATH = CONTENT_PATH / "templates"
GUIDES_PATH = CONTENT_PATH / "guides"
exclude_guides = ["README.md", "ERROR.md"]
templates = Jinja2Templates(directory=str(TEMPLATES_PATH))