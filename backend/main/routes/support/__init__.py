from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
import os
import json
import re
import threading
from sentence_transformers import SentenceTransformer
import numpy as np
from limiter import limiter

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

# --- Parse FAQ section ---
def parse_faq_section(context_text: str) -> dict:
    """Parse FAQ section from the context and return a map of questions to answers."""
    faq_map = {}
    
    # Find the FAQ section
    faq_match = re.search(r'## FAQ\s*\n(.*)', context_text, re.DOTALL)
    if not faq_match:
        print("Warning: FAQ section not found in context")
        return faq_map
    
    faq_content = faq_match.group(1)
    print(f"Found FAQ section, length: {len(faq_content)}")
    
    # Simple approach: use the working regex pattern
    qa_pattern = r'- Вопрос:\s*((\s*>.*$)*)\s*Ответ:\s*((\s*>.*$)*)'
    matches = re.findall(qa_pattern, faq_content, re.MULTILINE)
    print(f"Found {len(matches)} FAQ matches")
    
    for i, match in enumerate(matches, 1):
        question_raw = match[0].strip()  # Group 1: question
        answer_raw = match[2].strip()    # Group 3: answer
        
        print(f"Processing match {i}:")
        print(f"  Raw question: '{question_raw}'")
        print(f"  Raw answer: '{answer_raw[:100]}...'")
        
        # Clean up question (remove > and normalize)
        question = re.sub(r'^\s*>\s*', '', question_raw)  # Remove first >
        question = re.sub(r'\n\s*>\s*', '\n', question)  # Replace subsequent > with newlines
        question = re.sub(r'\n+', ' ', question)  # Replace multiple newlines with spaces
        question = question.strip()
        
        # Clean up answer (remove > and normalize)
        answer = re.sub(r'^\s*>\s*', '', answer_raw)  # Remove first >
        answer = re.sub(r'\n\s*>\s*', '\n', answer)  # Replace subsequent > with newlines
        answer = re.sub(r'\n+', ' ', answer)  # Replace multiple newlines with spaces
        answer = answer.strip()
        
        faq_map[question] = answer
        print(f"  Clean question: '{question}'")
        print(f"  Clean answer: '{answer[:100]}...'")
    
    print(f"Total FAQ entries parsed: {len(faq_map)}")
    return faq_map

# Parse FAQ at startup
faq_map = parse_faq_section(full_context)

# Global variables for sentence transformer model
model = None
faq_embeddings = None
faq_questions = None
model_loading = False
model_loaded = False

def load_sentence_transformer():
    """Load sentence transformer model in a background thread."""
    global model, faq_embeddings, faq_questions, model_loading, model_loaded
    
    if model_loading or model_loaded:
        return
    
    model_loading = True
    
    try:
        print("Loading sentence transformer model...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("Model loaded successfully!")
        
        # Mark model as loaded but don't encode questions yet
        model_loaded = True
        faq_questions = list(faq_map.keys())
        print(f"FAQ map has {len(faq_map)} entries, questions: {faq_questions}")
        
        # Encode questions in background (non-blocking for server startup)
        print(f"Encoding {len(faq_questions)} FAQ questions in background...")
        faq_embeddings = model.encode(faq_questions)
        print("FAQ questions encoded successfully!")
        
    except Exception as e:
        print(f"Warning: Could not load sentence transformer model: {e}")
        import traceback
        traceback.print_exc()
        model = None
        faq_embeddings = None
        faq_questions = None
    finally:
        model_loading = False

# Start loading the model in a background thread
threading.Thread(target=load_sentence_transformer, daemon=True).start()

def find_matching_faq_question(user_question: str, faq_map: dict) -> str:
    """Find a matching FAQ question using sentence transformers for semantic similarity."""
    global model, faq_embeddings, faq_questions, model_loaded
    
    # If model is not loaded yet, return None (will use OpenRouter API)
    if not model_loaded or model is None:
        return None
    
    # If embeddings are not ready yet, encode them now (lazy loading)
    if faq_embeddings is None and faq_questions is not None:
        try:
            print("Encoding FAQ questions on-demand...")
            faq_embeddings = model.encode(faq_questions)
            print("FAQ questions encoded successfully!")
        except Exception as e:
            print(f"Error encoding FAQ questions: {e}")
            return None
    
    # If still no embeddings, fall back to OpenRouter
    if faq_embeddings is None:
        return None
    
    try:
        # Encode the user question
        user_embedding = model.encode([user_question], show_progress_bar=False)
        
        # Calculate cosine similarities
        similarities = np.dot(faq_embeddings, user_embedding.T).flatten()
        
        # Find the best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        
        # Return match if similarity is above threshold
        threshold = 0.7  # Adjust this threshold as needed
        if best_similarity >= threshold:
            return faq_questions[best_idx]
    except Exception as e:
        print(f"Error in sentence transformer matching: {e}")
    
    return None

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
    # Check if we have a matching FAQ answer
    matching_question = find_matching_faq_question(message, faq_map)
    if matching_question:
        answer = faq_map[matching_question]
        yield f"data: {json.dumps({'content': answer})}\n\n"
        return
    
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

@router.post("/chat")
@limiter.limit("1/second")
@limiter.limit("20/day")
async def chat(request: Request, chat_request: ChatRequest):
    return StreamingResponse(
        generate_response(chat_request.session_id, chat_request.message),
        media_type="text/plain"
    )