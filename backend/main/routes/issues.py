import os
import time

import httpx
import jwt
from fastapi import APIRouter, Request, HTTPException
from httpx import HTTPStatusError

from models import ReportCrash
from utils import trim_margin

router = APIRouter()

GITHUB_API_URL = "https://api.github.com/repos/Toolbox-io/Toolbox-io/issues"
GITHUB_API_VERSION = os.getenv("GITHUB_API_VERSION", "2022-11-28")  # Example version
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID")
GITHUB_PRIVATE_KEY = os.getenv("GITHUB_PRIVATE_KEY")


def generate_jwt(app_id: str, private_key: str) -> str:
    now = int(time.time())
    payload = {
        "iat": now - 60,
        "exp": now + (10 * 60),
        "iss": app_id
    }
    # If the key is stored with literal \n, convert to real newlines
    if "\\n" in private_key:
        private_key = private_key.replace("\\n", "\n")
    return jwt.encode(payload, private_key, algorithm="RS256")

async def get_installation_access_token(jwt_token: str, installation_id: str) -> str:
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers)
        response.raise_for_status()
        return response.json()["token"]

@router.post("/reportCrash")
async def report_crash(
    request: Request,
    crash_report: ReportCrash
):
    issueBody = f"""
        |_Этот отчет об ошибке был автоматически отправлен через Toolbox.io._
        |
        |### Конфигурация
        |**Версия Android:** {crash_report.androidVersion}
        |**Производитель:** {crash_report.manufacturer}
        |**Бренд:** {crash_report.brand}
        |**Модель:** {crash_report.model}
        |**Версия Toolbox.io**: {crash_report.programVersion}
        |
        |### Ошибка
        |```
        |{crash_report.exceptionStacktrace}
        |```
    """

    whatHappened = crash_report.whatHappened.strip()
    if whatHappened != "":
        processed = "\n".join(f"> {line}" for line in whatHappened.splitlines())
        issueBody += f"""
            |
            |### Что делали?
            |{processed}
        """

    issueBody = trim_margin(issueBody.strip())

    payload = {
        "title": f"{crash_report.exceptionClass}: {crash_report.exceptionMsg}"[:256],
        "body": issueBody,
        "assignees": ["denis0001-dev"],
        "labels": ["приложение", "баг", "авто-отчет"]
    }

    # --- GitHub App Auth ---
    if not (GITHUB_APP_ID and GITHUB_INSTALLATION_ID and GITHUB_PRIVATE_KEY):
        raise HTTPException(status_code=500, detail="GitHub App credentials are not set in environment variables.")

    jwt_token = generate_jwt(GITHUB_APP_ID, GITHUB_PRIVATE_KEY)
    try:
        access_token = await get_installation_access_token(jwt_token, GITHUB_INSTALLATION_ID)
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())

    headers = {
        "Accept": "application/vnd.github.raw+json",
        "X-Github-Api-Version": GITHUB_API_VERSION,
        "Authorization": f"Bearer {access_token}"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(GITHUB_API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
    except HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.json())
