import os

from pydantic import BaseModel


class InvalidConfigError(Exception):
    def __init__(self, msg: str = "") -> None:
        self.msg = msg

    def __str__(self) -> str:
        return self.msg


class EnvConfig(BaseModel):
    secret_key: str
    log_level: str

    def __init__(self) -> None:
        if isinstance((key := os.getenv("secret")), str) and key.__len__() >= 32:
            self.secret_key = key
        else:
            raise InvalidConfigError(
                "Invalid secret key configuration. You should generate one by run command and set it into env `secret`: \n`openssl rand -hex 32`\n"
            )

        if isinstance((log := os.getenv("log")), str):
            self.log_level = log
        else:
            self.log_level = "INFO"

        super().__init__()

env = EnvConfig()
