import os
from pathlib import Path

import toml
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


class SecurityConfig(BaseModel):
    secret_key: str


class DataBaseConfig(BaseModel):
    host: str
    port: int
    name: str
    username: str
    password: str


class EmailConfig(BaseModel):
    host: str
    port: int
    address: str
    password: str


class LogConfig(BaseModel):
    log_level: str


class TestConfig(BaseModel):
    is_test: bool
    email: EmailConfig


class Config(BaseModel):
    security: SecurityConfig
    database: DataBaseConfig
    email: EmailConfig
    log: LogConfig = LogConfig(log_level="INFO")
    test: TestConfig | None = None

    @classmethod
    def load(cls):
        config_path = Path(
            os.path.join(os.getcwd()), "Services", "Config", "config.toml"
        )

        if not config_path.exists():
            raise FileNotFoundError("Config file not found.")

        config = toml.load(config_path)
        return cls.model_validate(config)


config = Config.load()
