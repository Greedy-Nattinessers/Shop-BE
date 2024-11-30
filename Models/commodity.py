from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ValidationError, model_validator


class Commodity(BaseModel):
    cid: str
    name: str
    price: float
    description: str
    image: str | None


class CreateCommodity(BaseModel):
    name: str
    price: float
    description: str

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls.model_validate_json(value)
        return value

    def to_commodity(self, cid: str, fid: str | None = None) -> Commodity:
        return Commodity(
            cid=cid,
            name=self.name,
            price=self.price,
            description=self.description,
            image=fid,
        )
