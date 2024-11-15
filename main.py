import logging
from os import name

from fastapi import FastAPI

import Services.Log.logger
from Services.Config.config import env

log = logging.getLogger("main")

app = FastAPI(title="Mall_BE")
