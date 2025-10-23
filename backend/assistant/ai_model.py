"""
AI Model functionality for the support assistant
Handles FAQ matching and AI response generation
"""

import os
import json
import re
import threading
import traceback
from typing import Dict, List, Generator
import numpy as np
from sentence_transformers import SentenceTransformer
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

# Global variables for sentence transformer model
model = None
faq_embeddings = None
faq_questions = None
model_loading = False
model_loaded = False

# Conversation history
conversation_history: Dict[str, List[Dict[str, str]]] = {}

def parse_faq_section(context_text: str) -> dict:
    """Parse FAQ section from context text and return a dictionary of questions and answers."""
    faq_map = {}
    
    # Split by FAQ section
    faq_section = re.search(r'## FAQ.*?(?=##|$)', context_text, re.DOTALL)
    if not faq_section:
        print("No FAQ section found in context")
        return faq_map
    
    faq_content = faq_section.group(0)
    
    # Find all Q: and A: pairs
    qa_pattern = r'Q:\s*(.*?)\s*A:\s*(.*?)(?=Q:|$)'
    matches = re.findall(qa_pattern, faq_content, re.DOTALL)
    
    for question, answer in matches:
        # Clean up the question and answer
        question = question.strip()
        answer = answer.strip()
        
        if question and answer:
            faq_map[question] = answer
    
    print(f"Total FAQ entries parsed: {len(faq_map)}")
    return faq_map

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
        
        # Encode questions in background (non-blocking for server startup)
        print(f"Encoding {len(faq_questions)} FAQ questions in background...")
        faq_embeddings = model.encode(faq_questions, show_progress_bar=False)
        print("FAQ questions encoded successfully!")
        
    except Exception as e:
        print(f"Warning: Could not load sentence transformer model: {e}")
        import traceback
        traceback.print_exc()
        model = None
        faq_questions = None
    finally:
        model_loading = False

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
            faq_embeddings = model.encode(faq_questions, show_progress_bar=False)
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
        threshold = 0.8  # Lowered threshold for better matching
        if best_similarity >= threshold:
            print(f"FAQ match found: '{faq_questions[best_idx]}' (similarity: {best_similarity:.3f})")
            return faq_questions[best_idx]
        else:
            print(f"No FAQ match: best match: '{faq_questions[best_idx]}' (similarity: {best_similarity:.3f})")
    except Exception as e:
        print(f"Error in sentence transformer matching: {e}")
    
    return None

def generate_response(session_id: str, message: str, faq_map: dict, instructions: str, full_context: str) -> Generator[str, None, None]:
    """Generate AI response for a user message."""
    # Get or create conversation history for this session
    if session_id not in conversation_history:
        conversation_history[session_id] = []

    # Check if we have a matching FAQ answer
    matching_question = find_matching_faq_question(message, faq_map)
    if matching_question:
        answer = faq_map[matching_question]
        yield f"data: {json.dumps({'content': answer})}\n\n"

        # Add the exchange to conversation history
        conversation_history[session_id].append({
            "role": "user",
            "content": message
        })
        conversation_history[session_id].append({
            "role": "assistant",
            "content": answer
        })
        
        return
    
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

    providers: List[Dict[str, str | List[str]]] = [
        {
            "base_url": "https://openrouter.ai/api/v1",
            "models": [
                "openai/gpt-oss-20b:free",
                "qwen/qwen3-coder:free",
                "mistralai/mistral-small-3.2-24b-instruct:free"
            ],
            "api_key": os.getenv("OPENAI_API_KEY")
        },
        {
            "base_url": "https://api.long-time.ru/v1",
            "models": [
                "deepseek-v3-250324",
                "chatgpt-4o-latest",
                "claude-sonnet-4-20250514",
                "grok-3-fast-latest",
                "gemini-2.5-flash"
            ],
            "api_key": "none"
        },
        {
            "base_url": "http://192.168.1.10:11434/v1",
            "models": [
                "gemma3:12b",
            ],
            "api_key": "none"
        }
    ]

    for provider in providers:
        print(f"Using provider: {provider['base_url']}")
        client = OpenAI(
            api_key=provider["api_key"],
            base_url=provider["base_url"]
        )

        for model in provider["models"]:
            try:
                print(f"Using model {model} from provider {provider['base_url']}")
                response: Stream[ChatCompletionChunk] = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )

                print("Streaming started successfully")
            
                full_response = ""
                for chunk in response:
                    if chunk.choices[0].delta.content is not None:
                        content = chunk.choices[0].delta.content
                        full_response += content
                        yield f"data: {json.dumps({'content': content})}\n\n"

                print("Response generation complete!")
                
                # Add the exchange to conversation history
                conversation_history[session_id].append({
                    "role": "user",
                    "content": message
                })
                conversation_history[session_id].append({
                    "role": "assistant",
                    "content": full_response
                })

                return
            except Exception as e: 
                print(f"Error using model {model} from provider {provider['base_url']}")
                traceback.print_exc()
    
    yield "data: {\"error\": \"All models failed\"}"

def initialize_ai_model(context_data: str, instructions: str):
    """Initialize the AI model with context and instructions."""
    global faq_map
    
    # Parse FAQ section
    faq_map = parse_faq_section(context_data)
    
    # Start loading the model in a background thread
    threading.Thread(target=load_sentence_transformer, daemon=True).start()
    
    return faq_map
