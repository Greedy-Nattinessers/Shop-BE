from enum import Enum

from pydantic import BaseModel


class Permission(int, Enum):
    Admin = 3
    Shop = 2
    User = 1

    def __lt__(self, value: int) -> bool:
        return self.value < value


class User(BaseModel):
    uid: str
    username: str
    email: str
    permission: Permission

    def __init__(self, uid: str, username: str, email: str, permission: int):
        super().__init__(
            uid=uid,
            username=username,
            email=email,
            permission=Permission(permission),
        )


class Token(BaseModel):
    access_token: str
    token_type: str
