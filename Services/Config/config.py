import os

from dotenv import load_dotenv


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


class EnvConfig:
    secret_key: str
    db_url: str
    db_name: str
    db_user: str
    db_password: str
    log_level: str = "INFO"

    def __init__(self) -> None:
        load_dotenv()

        required = ["secret_key", "db_url", "db_name", "db_user", "db_password"]
        normal = [("log_level", "INFO")]
        for req in required:
            if (v := os.getenv(req.upper())) is None or v == "":
                raise InvalidConfigError(
                    f"Invalid or missing {req} environment variable."
                )
            setattr(self, req, v)
        for norm in normal:
            if (v := os.getenv(norm[0].upper())) is None or v == "":
                setattr(self, norm[0], norm[1])
            else:
                setattr(self, norm[0], v)
        super().__init__()


config = EnvConfig()
