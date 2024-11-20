import logging
from datetime import timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from Models.database import UserDb
from Models.response import ExceptionResponse, StandardResponse
from Models.user import Token
from Services.Database.database import get_db
from Services.Limiter.limiter import limiter
from Services.Security.user import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token

user_router = APIRouter(prefix="/user")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger("user")


@user_router.post("/register", response_model=StandardResponse)
@limiter.limit("5/minute")
async def user_reg(
    request: Request,
    email: str = Form(),
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
) -> StandardResponse:
    if (
        db.query(UserDb)
        .filter(UserDb.email == email or UserDb.username == username)
        .first()
        is not None
    ):
        raise HTTPException(status_code=400, detail="User already exists")

    db.add(
        UserDb(
            uid=uuid4().hex,
            email=email,
            username=username,
            password=pwd_ctx.hash(password),
        )
    )
    db.commit()
    return StandardResponse(status_code=201, message="User created")


@user_router.post("/login", response_model=StandardResponse)
@limiter.limit("5/minute")
async def user_login(
    request: Request,
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
) -> StandardResponse[Token]:
    user: UserDb | None = db.query(UserDb).filter(UserDb.username == username).first()

    if user is None or not pwd_ctx.verify(password, user.password):
        raise ExceptionResponse.AUTH_FAILED

    token = create_access_token(
        data={"sub": user.email, "id": user.uid},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )

    return StandardResponse[Token](data=Token(access_token=token, token_type="bearer"))
