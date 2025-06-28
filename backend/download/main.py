from typing import Optional

import httpx
from fastapi import HTTPException, FastAPI
from fastapi.responses import RedirectResponse

GITHUB_API = "https://api.github.com/repos/Toolbox-io/Toolbox-io"

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

async def get_release_asset_url(version: Optional[str] = None) -> Optional[str]:
    async with httpx.AsyncClient() as client:
        if version is None or version == "latest" or version == "":
            url = f"{GITHUB_API}/releases/latest"
        else:
            url = f"{GITHUB_API}/releases/tags/v{version}"
        resp = await client.get(url)
        if resp.status_code != 200:
            return None
        data = resp.json()
        assets = data.get("assets", [])
        if not assets:
            return None
        return assets[0].get("browser_download_url")

@app.get("/{path:path}")
async def serve_files(path: str):
    # Handle /, /latest, /v<version>
    if path == "" or path == "/" or path == "latest":
        asset_url = await get_release_asset_url()
    elif path.startswith("v"):
        version = path[1:]
        asset_url = await get_release_asset_url(version)
    else:
        # Not a versioned or latest path, return 404
        raise HTTPException(status_code=404, detail="Not found")
    if asset_url:
        return RedirectResponse(asset_url)
    raise HTTPException(status_code=404, detail="Release or asset not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
