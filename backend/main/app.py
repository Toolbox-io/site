from urllib.request import Request

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

import utils
from limiter import limiter
from routes import auth, guides, core, issues

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)


# Rate limiting
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    # noinspection PyProtectedMember
    return await limiter._rate_limit_exceeded_handler(request, exc)
app.state.limiter = limiter
# noinspection PyTypeChecker
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)


# Add CORS middleware with proper security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://beta.toolbox-io.ru",
        "http://localhost:8000",
        "https://toolbox-io.ru"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


# Routes
app.include_router(auth.core.api_router, prefix="/api/auth")
app.include_router(auth.core.router)
app.include_router(auth.management.router, prefix="/api/auth")
app.include_router(core.router)
app.include_router(guides.router)
app.include_router(utils.router)
app.include_router(issues.router, prefix="/api/issues")