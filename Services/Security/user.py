from datetime import UTC, datetime, timedelta

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from Models.database import UserDb
from Models.response import ExceptionResponse
from Models.user import User
from Services.Config.config import config
from Services.Database.database import get_db
from Services.Log.logger import logging

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = config.secret_key
log = logging.getLogger("security")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: str = payload["id"]
        if uid is None:
            raise ExceptionResponse.AUTH_FAILED
    except JWTError:
        raise ExceptionResponse.AUTH_FAILED

    user: UserDb | None = db.query(UserDb).filter(UserDb.uid == uid).first()
    if user is None:
        raise ExceptionResponse.AUTH_FAILED
    return User(uid=user.uid, username=user.username, email=user.email)