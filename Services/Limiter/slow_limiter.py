from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from Models.response import HTTPException

freq_limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def RateLimitExceeded_handler(request: Request, exc: RateLimitExceeded):
    raise HTTPException(429, f"Rate limit exceeded: {exc.detail}")
