import logging

import fastapi
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
from rich.logging import RichHandler

from Services.Config.config import config

logging.basicConfig(
    level=config.log_level,
    format="%(asctime)s - %(name)s [%(levelname)s] : %(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, tracebacks_suppress=[fastapi]),
        ConcurrentTimedRotatingFileHandler("Logs/latest.log", when="midnight", interval=1),
    ],
)
