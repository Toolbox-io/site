from starlette.responses import RedirectResponse

from app import app


@app.get("/login")
async def login(): return RedirectResponse("/account/login", status_code=308)

@app.get("/register")
async def register(): return RedirectResponse("/account/register", status_code=308)