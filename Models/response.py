from fastapi import HTTPException, status
from pydantic import BaseModel


class ExceptionResponse:
    AUTH_FAILED = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    PERMISSION_DENIED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )

    NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not found",
    )


class StandardResponse[T](BaseModel):
    """
    Standard Response Model
    ~~~~~~~~~~~~~~~~~~~~~
    This model is the default web response format of the API.
    """

    status_code: int
    message: str | None
    data: T | None

    def __init__(
        self, status_code: int = 200, message: str | None = None, data: T | None = None
    ):
        super().__init__(status_code=status_code, message=message, data=data)
