from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from Routers.shop import shop_router
from Routers.user import user_router
from Services.Limiter.limiter import limiter
from Services.Log.logger import logging

log = logging.getLogger("main")

app = FastAPI(title="Shop_BE")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore

app.include_router(user_router)
app.include_router(shop_router)