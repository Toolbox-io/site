import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse, FileResponse

router = APIRouter()

GITHUB_API = "https://api.github.com/repos/Toolbox-io/Toolbox-io"
CACHE = Path("./cache").resolve()

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

async def github_api(url: str) -> tuple[Optional[any], bool]:
    cache_file = CACHE / "responses.json"
    logging.info(f"[github_api] Checking cache file at {cache_file}")
    if not cache_file.exists():
        logging.info(f"[github_api] Cache file does not exist, creating new one.")
        cache_file.write_text("{}")
    lock = asyncio.Lock()
    async with lock:
        try:
            with open(cache_file, "r") as f:
                cache = json.load(f)
            if not isinstance(cache, dict):
                logging.info(f"[github_api] Cache file is not a dict, resetting.")
                cache = {}
        except Exception as e:
            logging.error(f"[github_api] Failed to load cache: {e}")
            cache = {}
    logging.info(f"[github_api] Trying to reuse the cache for URL: {url}")
    etag = cache.get(url, {}).get("etag")
    headers = {"If-None-Match": etag} if etag else {}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        logging.info(f"[github_api] HTTP status: {response.status_code} for {url}")
        if response.status_code == 304 and url in cache:
            logging.info(f"[github_api] Using cached response for {url}")
            return cache[url]["response"], True
        if response.status_code != 200:
            logging.error(f"[github_api] Non-200 response for {url}: {response.status_code}")
            return None, False
        new_etag = response.headers.get("etag")
        data = response.json()
        if new_etag:
            logging.info(f"[github_api] New ETag for {url}: {new_etag}, updating cache.")
            cache[url] = {"etag": new_etag, "response": data}
            async with lock:
                with open(cache_file, "w") as f:
                    json.dump(cache, f)
        logging.info(f"[github_api] Returning new data for {url}")
        return data, False

async def get_release_asset_url(version: Optional[str] = None) -> tuple[Optional[str], bool, Optional[str]]:
    async def run() -> tuple[Optional[any], bool, Optional[str]]:
        if version in [None, "latest", "", "/"]:
            url = f"{GITHUB_API}/releases/latest"
        else:
            url = f"{GITHUB_API}/releases/tags/v{version.removeprefix('v')}"
        logging.info(f"[get_release_asset_url] Fetching release info from {url}")
        data, from_cache = await github_api(url)
        if not data:
            logging.error(f"[get_release_asset_url] No data for {url}")
            return None, from_cache, None
        assets = data.get("assets", [])
        if not assets:
            logging.error(f"[get_release_asset_url] No assets found in release data for {url}")
            return None, from_cache, data.get("tag_name")
        asset_url = assets[0].get("browser_download_url")
        tag_name = data.get("tag_name")
        logging.info(f"[get_release_asset_url] Asset URL: {asset_url} (from_cache={from_cache}, tag_name={tag_name})")
        return asset_url, from_cache, tag_name

    for _ in range(3):
        result = await run()
        if not result[0]:
            logging.info(f"[get_release_asset_url] No result, trying fallback version")
            version = f"{version.removesuffix('.')}.0"
        else:
            return result
    logging.error(f"[get_release_asset_url] Failed to get asset URL after retries")
    return None, False, None

@router.get("/download/{path:path}")
async def serve_files(path: str):
    logging.info(f"[serve_files] Requested path: {path}")
    asset_url, from_cache, tag_name = await get_release_asset_url(path)
    if asset_url:
        assets_dir = CACHE / "assets"
        assets_dir.mkdir(parents=True, exist_ok=True)
        filename = os.path.basename(asset_url)
        asset_path = assets_dir / filename
        logging.info(f"[serve_files] Asset path: {asset_path}")
        # Use tag_name for download filename if available
        version = tag_name or path.strip("/").replace("/", "_") or "latest"
        download_name = f"Toolbox.io.{version}.apk"
        if from_cache and asset_path.exists():
            logging.info(f"[serve_files] Serving cached asset file: {asset_path} as {download_name}")
            return FileResponse(asset_path, media_type="application/vnd.android.package-archive", filename=download_name)
        logging.info(f"[serve_files] Asset not cached, redirecting to {asset_url} and downloading in background")
        # Start background download
        async def download_asset(url, path):
            try:
                start = time.time()
                async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                    resp = await client.get(url)
                download_time = time.time() - start
                logging.info(f"[background_download] Download status: {resp.status_code}, took {download_time:.2f}s")
                if resp.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(resp.content)
                    logging.info(f"[background_download] Saved asset to {path}")
                else:
                    logging.error(f"[background_download] Failed to download asset: {url}")
            except Exception as e:
                logging.error(f"[background_download] Exception: {e}")
        asyncio.create_task(download_asset(asset_url, asset_path))
        return RedirectResponse(url=asset_url, status_code=308)
    logging.error(f"[serve_files] Asset not found for path: {path}")
    raise HTTPException(status_code=404)
