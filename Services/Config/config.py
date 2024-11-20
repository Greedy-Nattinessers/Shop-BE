import os

from dotenv import load_dotenv
from pydantic import BaseModel


class InvalidConfigError(Exception):
    """
    InvalidConfigError
    ------------------
    Raised when a required environment variable is not set or is invalid.
    """

    def __init__(self, msg: str = "") -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class EnvConfig(BaseModel):
    secret_key: str
    db_url: str
    db_name: str
    db_user: str
    db_password: str
    log_level: str = "INFO"

    def __init__(self) -> None:
        load_dotenv()

        required = ["secret_key", "db_url", "db_name", "db_user", "db_password"]
        normal = ["log_level"]
        for req in required:
            if (value := os.getenv(req.upper())) is None:
                raise InvalidConfigError(f"Missing environment variable: {req}")
            self.__setattr__(req, value)
        for norm in normal:
            if (value := os.getenv(norm.upper())) is not None:
                self.__setattr__(norm, value)
        super().__init__()


config = EnvConfig()
