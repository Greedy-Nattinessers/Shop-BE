from enum import Enum

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class BaseResponse[T](BaseModel):
    """
    Base Response Class
    ~~~~~~~~~~~~~~~~~~~~~~
    This class is the base response of the API.
    """

    status_code: int
    message: str | None = None
    data: T | None = None


class StandardResponse[T](JSONResponse):
    """
    Standard Response Class
    ~~~~~~~~~~~~~~~~~~~~~~
    This class is the default web response of the API.
    """

    def __init__(
        self,
        status_code: int = 200,
        message: str | None = None,
        data: T | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            content=BaseResponse[T](
                status_code=status_code, message=message, data=data
            ).model_dump(mode="json"),
            status_code=status_code,
            headers=headers,
        )


class ExceptionResponseEnum(Enum):
    """
    Exception Response Enum
    ~~~~~~~~~~~~~~~~~~~~~~
    This enum is the collection of static exception responses for the API.
    """

    AUTH_FAILED = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    CAPTCHA_FAILED = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Captcha validation failed",
    )

    PERMISSION_DENIED = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Permission denied",
    )

    NOT_FOUND = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not found",
    )

    INVALID_OPERATION = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid operation",
    )

    RESOURCE_CONFILCT = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Resource conflict",
    )

    def __call__(self) -> HTTPException:
        return self.value


async def http_exception_handler(request, exc: HTTPException) -> StandardResponse[None]:
    return StandardResponse[None](
        status_code=exc.status_code, message=exc.detail, data=None
    )


async def validation_exception_handler(
    request, exc: RequestValidationError
) -> StandardResponse[object]:
    return StandardResponse[object](
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Invalid request data structure.",
        data=jsonable_encoder(exc.errors()),
    )
