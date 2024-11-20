from pydantic import BaseModel


class User(BaseModel):
    uid: str
    username: str
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str
