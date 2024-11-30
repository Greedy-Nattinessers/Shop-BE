from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from Routers.shop import shop_router
from Routers.user import user_router
from Services.Limiter.size_limiter import LimitUploadSize
from Services.Limiter.slow_limiter import freq_limiter
from Services.Log.logger import logging

log = logging.getLogger("main")

app = FastAPI(title="Shop_BE")
app.state.limiter = freq_limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.add_middleware(LimitUploadSize, max_upload_size=1024 * 1024 * 10)  # ~10MB

app.include_router(user_router)
app.include_router(shop_router)
