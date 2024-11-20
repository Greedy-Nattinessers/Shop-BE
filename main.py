from os import name

from fastapi import FastAPI

from Services.Log.logger import logging

log = logging.getLogger("main")

app = FastAPI(title="Mall_BE")
