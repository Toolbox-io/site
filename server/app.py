from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include authentication routes
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"]) 