from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

import utils
from limiter import limiter
from routes import auth, auth_api_r, core, guides, mail


async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    # noinspection PyProtectedMember
    return await limiter._rate_limit_exceeded_handler(request, exc)

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# Add rate limiting exception handler
app.state.limiter = limiter
# noinspection PyTypeChecker
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add CORS middleware with proper security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://beta.toolbox-io.ru",
        "http://localhost:8000"   # For local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth_api_r.router, prefix="/api/auth")
app.include_router(auth.router)
app.include_router(core.router)
app.include_router(guides.router)
app.include_router(utils.router)
app.include_router(mail.router)