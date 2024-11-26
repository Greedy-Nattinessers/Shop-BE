from enum import Enum

from pydantic import BaseModel


class Permission(int, Enum):
    Admin = 2
    User = 1
    Guest = 0

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


class UpdateUser(BaseModel):
    uid: str
    password: str | None
    new_password: str | None
    permission: Permission | None

    def __init__(
        self,
        uid: str,
        password: str | None = None,
        new_password: str | None = None,
        permission: int | None = None,
    ):
        super().__init__(
            uid=uid,
            password=password,
            new_password=new_password,
            permission=Permission(permission) if permission is not None else None,
        )


class Token(BaseModel):
    access_token: str
    token_type: str
