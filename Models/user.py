from datetime import date
from enum import Enum

from pydantic import BaseModel


class Permission(int, Enum):
    ADMIN = 2
    USER = 1
    GUEST = 0

    def __lt__(self, value: int) -> bool:
        return self.value < value

    def __call__(self) -> int:
        return self.value


class Gender(int, Enum):
    MALE = 1
    FEMALE = 0


class User(BaseModel):
    uid: str
    username: str
    email: str
    permission: Permission
    birthday: date | None
    gender: Gender
    aid: str | None


class AddressBase(BaseModel):
    name: str
    phone: str
    address: str


class UserAddress(AddressBase):
    aid: str
    uid: str


class UpdateUser(BaseModel):
    birthday: date | None = None
    gender: Gender | None = None
    password: str | None = None
    permission: Permission | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
