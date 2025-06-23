from fastapi import APIRouter
from starlette.responses import RedirectResponse

router = APIRouter()

@router.get("/login")
async def login(): return RedirectResponse("/account/login", status_code=308)

@router.get("/register")
async def register(): return RedirectResponse("/account/register", status_code=308)