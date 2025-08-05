from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
import os
import json
from limiter import limiter
from ai_cache import cache_manager

router = APIRouter()

# --- Load Context and Instructions ---
try:
    with open("routes/support/context/data.md", "r") as f:
        full_context = f.read()
except FileNotFoundError:
    print("Error: routes/support/context/data.md not found.")
    exit()

try:
    with open("routes/support/context/instruction.md", "r") as f:
        instructions = f.read()
except FileNotFoundError:
    print("Error: routes/support/context/instruction.md not found.")
    exit()

# --- OpenAI client setup ---
client = OpenAI(
    api_key=os.getenv("AI_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

# --- Conversation history ---
conversation_history = {}

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=1024, description="Message content (max 1024 characters)")
    session_id: str = Field(default="default", description="Session ID for conversation history")

def generate_response(session_id: str, message: str):
    # Get or create conversation history for this session
    if session_id not in conversation_history:
        conversation_history[session_id] = []
    
    # Prepare messages with conversation history
    messages = [
        {
            "role": "system",
            "content": f"{instructions}\n\n## Контекст\n\n{full_context}"
        }
    ]
    
    # Add conversation history
    messages.extend(conversation_history[session_id])
    
    # Add current message
    messages.append({
        "role": "user",
        "content": message
    })

    try:
        response: Stream[ChatCompletionChunk] = client.chat.completions.create(
            model="qwen/qwen3-coder:free",
            messages=messages,
            stream=True
        )
        
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                full_response += content
                yield f"data: {json.dumps({'content': content})}\n\n"
        
        # Add the exchange to conversation history
        conversation_history[session_id].append({
            "role": "user",
            "content": message
        })
        conversation_history[session_id].append({
            "role": "assistant",
            "content": full_response
        })
        
    except Exception as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"

def generate_cached_response(session_id: str, message: str):
    """Generate response from cache and stream it"""
    # Get conversation history for this session
    session_history = conversation_history.get(session_id, [])
    
    # Check cache with conversation context
    cached_response = cache_manager.check_cache(
        message, 
        instructions, 
        full_context, 
        session_history
    )
    
    if cached_response:
        # Stream cached response character by character to simulate real response
        for char in cached_response:
            yield f"data: {json.dumps({'content': char})}\n\n"
    else:
        # Generate new response and cache it
        full_response = ""
        for chunk in generate_response(session_id, message):
            if chunk.startswith("data: "):
                try:
                    data = json.loads(chunk[6:])
                    if 'content' in data:
                        content = data['content']
                        full_response += content
                        yield chunk
                except json.JSONDecodeError:
                    yield chunk
        
        # Store response in cache (background) with conversation history
        cache_manager.store_response(
            message, 
            full_response, 
            instructions, 
            full_context, 
            session_history
        )

@router.post("/chat")
@limiter.limit("1/second")
@limiter.limit("20/day")
async def chat(request: Request, chat_request: ChatRequest):
    return StreamingResponse(
        generate_cached_response(chat_request.session_id, chat_request.message),
        media_type="text/plain"
    )

@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics"""
    return cache_manager.get_cache_stats()

@router.delete("/cache")
async def invalidate_cache():
    """Invalidate entire cache"""
    cache_manager.invalidate_cache()
    return {"message": "Cache invalidated successfully"}