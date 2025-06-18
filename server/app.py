from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from limiter import limiter
from routes import auth

async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    # noinspection PyProtectedMember
    return await limiter._rate_limit_exceeded_handler(request, exc)

app = FastAPI()

# Add rate limiting exception handler
app.state.limiter = limiter
# noinspection PyTypeChecker
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# Add CORS middleware with proper security
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://server.toolbox-io.ru",
        "http://localhost:8000"   # For local development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"]) 