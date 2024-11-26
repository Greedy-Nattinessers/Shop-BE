from uuid import uuid4

from pydantic import BaseModel


class Commodity(BaseModel):
    cid: str
    name: str
    price: float
    description: str


class CreateCommodity(BaseModel):
    name: str
    price: float
    description: str

    def to_commodity(self) -> Commodity:
        return Commodity(
            cid=uuid4().hex,
            name=self.name,
            price=self.price,
            description=self.description,
        )
