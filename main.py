from fastapi import FastAPI

from Routers.user import user_router
from Services.Log.logger import logging

log = logging.getLogger("main")

app = FastAPI(title="Shop_BE")


app.include_router(user_router)
