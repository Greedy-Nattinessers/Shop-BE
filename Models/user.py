from enum import Enum
from uuid import uuid4

from pydantic import BaseModel


class Permission(int, Enum):
    ADMIN = 2
    USER = 1
    GUEST = 0

    def __lt__(self, value: int) -> bool:
        return self.value < value

    def __call__(self) -> int:
        return self.value


class User(BaseModel):
    uid: str
    username: str
    email: str
    permission: Permission


class UserAddress(BaseModel):
    aid: str
    uid: str
    name: str
    phone: str
    address: str
    is_default: bool


class AddressRequest(BaseModel):
    name: str
    phone: str
    address: str
    is_default: bool

    def to_address(self, uid: str) -> UserAddress:
        return UserAddress(
            aid=uuid4().hex,
            uid=uid,
            phone=self.phone,
            name=self.name,
            address=self.address,
            is_default=self.is_default,
        )


class UpdateUser(BaseModel):
    password: str | None = None
    permission: Permission | None = None


class Token(BaseModel):
    access_token: str
    token_type: str
