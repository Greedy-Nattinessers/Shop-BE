from pydantic import BaseModel, model_validator


class BaseCommodity(BaseModel):
    cid: str
    name: str
    price: float
    album: str | None


class Commodity(BaseCommodity):
    description: str | None
    images: list[str]


class CartCommodity(BaseCommodity):
    count: int


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


class UpdateCommodity(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls.model_validate_json(value)
        return value
