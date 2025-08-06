from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
import os

INTERNAL_BOT_TOKEN = os.getenv("INTERNAL_BOT_TOKEN")

def user_id_key_func(request: Request):
    internal_token = request.headers.get("X-Internal-Token")
    user_id = request.headers.get("X-User-ID")
    if internal_token and INTERNAL_BOT_TOKEN and internal_token == INTERNAL_BOT_TOKEN and user_id:
        return user_id
    return get_remote_address(request)

# Initialize rate limiter with default key_func (IP-based)
limiter = Limiter(key_func=get_remote_address)