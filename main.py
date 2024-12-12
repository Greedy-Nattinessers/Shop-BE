from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from Models.response import http_exception_handler
from Routers.shop import shop_router
from Routers.user import user_router
from Services.Limiter.size_limiter import LimitUploadSize
from Services.Limiter.slow_limiter import RateLimitExceeded_handler, freq_limiter
from Services.Log.logger import logging

log = logging.getLogger("main")

app = FastAPI(title="Shop_BE")
app.state.limiter = freq_limiter
app.add_exception_handler(RateLimitExceeded, RateLimitExceeded_handler)  # type: ignore
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LimitUploadSize, max_upload_size=1024 * 1024 * 10)  # ~10MB

app.include_router(user_router)
app.include_router(shop_router)
