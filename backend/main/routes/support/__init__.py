from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from limiter import limiter, user_id_key_func

router = APIRouter()

class ChatRequest(BaseModel):
    message: str = Field(..., description="User message")
    session_id: str = Field(default="default", description="Session ID for conversation history")

@router.post("/chat")
@limiter.limit("1/second", key_func=user_id_key_func)
@limiter.limit("20/day", key_func=user_id_key_func)
async def chat(request: Request, chat_request: ChatRequest):
    """Support chat endpoint - AI functionality moved to assistant service"""
    return JSONResponse({
        "message": "AI support functionality has been moved to the assistant service. Please contact support through Telegram bot.",
        "status": "moved"
    })