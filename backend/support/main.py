from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import json

app = FastAPI()

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

# --- Rate limiting setup ---
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Load Context and Instructions ---
try:
    with open("context/data.md", "r") as f:
        full_context = f.read()
except FileNotFoundError:
    print("Error: context/data.md not found.")
    exit()

try:
    with open("context/instruction.md", "r") as f:
        instructions = f.read()
except FileNotFoundError:
    print("Error: context/instruction.md not found.")
    exit()

# --- OpenAI client setup ---
client = OpenAI(
    api_key=os.getenv("API_KEY"),
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

@app.post("/chat")
@limiter.limit("1/second")
@limiter.limit("20/day")
async def chat(request: Request, chat_request: ChatRequest):
    return StreamingResponse(
        generate_response(chat_request.session_id, chat_request.message),
        media_type="text/plain"
    )

@app.get("/")
async def root():
    return {"message": "Toolbox.io Support Bot API"}

@app.get("/test_api")
async def test_api():
    return FileResponse("./test_api.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)