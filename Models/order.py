from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class OrderStatus(int, Enum):
    Idle = 0
    Shipped = 1
    Finished = 2
    Canceled = 3


class OrderBase(BaseModel):
    aid: str
    content: dict[str, int]


class Order(OrderBase):
    uid: str
    oid: str
    time: datetime
    status: OrderStatus
