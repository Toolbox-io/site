import os
import json
import hashlib
import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
import threading
import time

class AICacheManager:
    def __init__(self, cache_dir: str = "/root/site/backend/main/data/ai_response_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize sentence transformer for semantic search
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Cache file paths
        self.cache_file = self.cache_dir / "responses.json"
        self.embeddings_file = self.cache_dir / "embeddings.pkl"
        
        # Load existing cache
        self.cache = self._load_cache()
        self.embeddings = self._load_embeddings()
        
        # Thread lock for thread-safe operations
        self.lock = threading.Lock()
    
    def _load_cache(self) -> Dict:
        """Load cache from JSON file"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}
    
    def _save_cache(self):
        """Save cache to JSON file"""
        with self.lock:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
    
    def _load_embeddings(self) -> Dict[str, np.ndarray]:
        """Load embeddings from pickle file"""
        if self.embeddings_file.exists():
            try:
                with open(self.embeddings_file, 'rb') as f:
                    return pickle.load(f)
            except (pickle.PickleError, IOError):
                return {}
        return {}
    
    def _save_embeddings(self):
        """Save embeddings to pickle file"""
        with self.lock:
            with open(self.embeddings_file, 'wb') as f:
                pickle.dump(self.embeddings, f)
    
    def _compute_hash(self, text: str) -> str:
        """Compute SHA-256 hash of text"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get embedding for text"""
        return self.model.encode(text)
    
    def _cosine_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Compute cosine similarity between two embeddings"""
        return np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    
    def _create_context_key(self, question: str, conversation_history: List[Dict]) -> str:
        """Create a context-aware key that includes conversation history"""
        # Create a context string from conversation history
        context_parts = []
        for msg in conversation_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            context_parts.append(f"{role}: {content}")
        
        # Combine question with conversation context
        context_string = f"QUESTION: {question}\nCONTEXT: {' | '.join(context_parts)}"
        return self._compute_hash(context_string)
    
    def _get_conversation_embedding(self, conversation_history: List[Dict]) -> np.ndarray:
        """Get embedding for conversation history"""
        if not conversation_history:
            return self._get_embedding("")
        
        # Create a single string representation of the conversation
        conversation_text = ""
        for msg in conversation_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            conversation_text += f"{role}: {content}\n"
        
        return self._get_embedding(conversation_text)
    
    def _find_semantic_match(self, question: str, conversation_history: List[Dict], threshold: float = 0.95) -> Optional[str]:
        """Find semantic match for question in cache, considering conversation context"""
        # Create context-aware embedding
        context_key = self._create_context_key(question, conversation_history)
        context_embedding = self._get_embedding(context_key)
        
        best_match = None
        best_similarity = 0.0
        
        for cache_id, embedding in self.embeddings.items():
            similarity = self._cosine_similarity(context_embedding, embedding)
            if similarity > best_similarity and similarity >= threshold:
                best_similarity = similarity
                best_match = cache_id
        
        return best_match
    
    def _conversation_similarity(self, history1: List[Dict], history2: List[Dict], threshold: float = 0.90) -> bool:
        """Check if two conversation histories are semantically similar"""
        if len(history1) != len(history2):
            return False
        
        # Get embeddings for both conversation histories
        embedding1 = self._get_conversation_embedding(history1)
        embedding2 = self._get_conversation_embedding(history2)
        
        # Calculate similarity
        similarity = self._cosine_similarity(embedding1, embedding2)
        return similarity >= threshold
    
    def check_cache(self, question: str, system_prompt: str, context: str, conversation_history: List[Dict] = None) -> Optional[str]:
        """
        Check if question exists in cache with matching system prompt, context, and semantically similar conversation history.
        Returns cached response if found, None otherwise.
        """
        if conversation_history is None:
            conversation_history = []
        
        # Compute hashes
        system_hash = self._compute_hash(system_prompt)
        context_hash = self._compute_hash(context)
        
        # Find semantic match for question with conversation context
        cache_id = self._find_semantic_match(question, conversation_history)
        
        if cache_id and cache_id in self.cache:
            cached_item = self.cache[cache_id]
            
            # Check if system prompt and context hashes match
            if (cached_item['system_hash'] == system_hash and 
                cached_item['context_hash'] == context_hash):
                
                # Check if conversation histories are semantically similar
                cached_history = cached_item.get('conversation_history', [])
                if self._conversation_similarity(conversation_history, cached_history):
                    return cached_item['response']
        
        return None
    
    def store_response(self, question: str, response: str, system_prompt: str, context: str, conversation_history: List[Dict] = None):
        """Store response in cache with background processing"""
        if conversation_history is None:
            conversation_history = []
        
        # Start background thread for storage
        thread = threading.Thread(
            target=self._store_response_background,
            args=(question, response, system_prompt, context, conversation_history)
        )
        thread.daemon = True
        thread.start()
    
    def _store_response_background(self, question: str, response: str, system_prompt: str, context: str, conversation_history: List[Dict]):
        """Store response in cache (background thread)"""
        try:
            # Compute hashes
            system_hash = self._compute_hash(system_prompt)
            context_hash = self._compute_hash(context)
            
            # Generate cache ID using context-aware key
            context_key = self._create_context_key(question, conversation_history)
            cache_id = self._compute_hash(context_key + system_prompt + context)
            
            # Get embedding for context-aware key
            context_embedding = self._get_embedding(context_key)
            
            # Store in cache
            with self.lock:
                self.cache[cache_id] = {
                    'question': question,
                    'response': response,
                    'system_hash': system_hash,
                    'context_hash': context_hash,
                    'conversation_history': conversation_history,  # Store for debugging
                    'timestamp': time.time()
                }
                
                self.embeddings[cache_id] = context_embedding
                
                # Save to disk
                self._save_cache()
                self._save_embeddings()
                
        except Exception as e:
            print(f"Error storing response in cache: {e}")
    
    def invalidate_cache(self):
        """Invalidate entire cache"""
        with self.lock:
            self.cache = {}
            self.embeddings = {}
            
            # Remove cache files
            if self.cache_file.exists():
                self.cache_file.unlink()
            if self.embeddings_file.exists():
                self.embeddings_file.unlink()
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            'total_entries': len(self.cache),
            'cache_size_mb': self._get_cache_size(),
            'oldest_entry': min([item['timestamp'] for item in self.cache.values()]) if self.cache else None,
            'newest_entry': max([item['timestamp'] for item in self.cache.values()]) if self.cache else None
        }
    
    def _get_cache_size(self) -> float:
        """Get cache size in MB"""
        total_size = 0
        if self.cache_file.exists():
            total_size += self.cache_file.stat().st_size
        if self.embeddings_file.exists():
            total_size += self.embeddings_file.stat().st_size
        return total_size / (1024 * 1024)  # Convert to MB

# Global cache manager instance
cache_manager = AICacheManager() 