import logging
from datetime import timedelta
from uuid import uuid4

import bcrypt
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from Models.database import UserDb
from Models.response import ExceptionResponse, StandardResponse
from Models.user import Permission, Token, UpdateUser, User
from Services.Cache.cache import cache
from Services.Mail.mail import Purpose, send_captcha
from Services.Database.database import get_db
from Services.Limiter.limiter import limiter
from Services.Security.user import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    verify_user,
)

user_router = APIRouter(prefix="/user")
logger = logging.getLogger("user")


@user_router.post("/captcha")
@limiter.limit("1/minute")
async def user_req_captcha(request: Request, email: str = Form()) -> StandardResponse:
    ip = request.client.host if request.client else "Unknown"
    captcha = send_captcha(email, Purpose.REGISTER, ip)
    await cache.set(email, captcha, ttl=300)
    return StandardResponse(status_code=200, message="Captcha sent")


@user_router.post("/register", response_model=StandardResponse)
@limiter.limit("5/minute")
async def user_reg(
    request: Request,
    email: str = Form(),
    username: str = Form(),
    password: str = Form(),
    captcha: str = Form(),
    db: Session = Depends(get_db),
) -> StandardResponse:
    if (
        db.query(UserDb)
        .filter(UserDb.email == email or UserDb.username == username)
        .first()
        is not None
    ):
        raise HTTPException(status_code=400, detail="User already exists")

    if (cached_captcha := await cache.get(email)) is None or cached_captcha != captcha:
        raise ExceptionResponse.CAPTCHA_FAILED
    
    await cache.delete(email)

    db.add(
        UserDb(
            uid=uuid4().hex,
            email=email,
            username=username,
            password=bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt()),
            permission=Permission.User.value,
        )
    )
    db.commit()
    return StandardResponse(status_code=201, message="User created")


@user_router.post("/login", response_model=StandardResponse)
@limiter.limit("5/minute")
async def user_login(
    request: Request,
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> StandardResponse[Token]:
    user: UserDb | None = (
        db.query(UserDb).filter(UserDb.username == body.username).first()
    )

    if user is None or not bcrypt.checkpw(
        bytes(body.password, "utf-8"), bytes(user.password, "utf-8")
    ):
        raise ExceptionResponse.AUTH_FAILED

    token = create_access_token(
        data={"sub": user.email, "id": user.uid},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return StandardResponse[Token](data=Token(access_token=token, token_type="bearer"))


@user_router.put("/profile", response_model=StandardResponse)
async def user_update(
    body: UpdateUser,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse:
    if body.uid != user.uid and verify_user(user, Permission.Admin):
        raise ExceptionResponse.PERMISSION_DENIED

    if (record := db.query(UserDb).filter(UserDb.uid == body.uid).first()) is not None:
        if body.password is not None and body.new_password is not None:
            if not bcrypt.checkpw(
                bytes(body.password, "utf-8"), bytes(record.password, "utf-8")
            ):
                raise ExceptionResponse.AUTH_FAILED
            record.password = bcrypt.hashpw(
                bytes(body.new_password, "utf-8"), bcrypt.gensalt()
            ).decode("utf-8")

        if body.permission is not None:
            record.permission = body.permission
        db.commit()
        return StandardResponse(status_code=200, message="User updated")
    else:
        raise ExceptionResponse.NOT_FOUND
