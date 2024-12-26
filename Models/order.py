from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class OrderStatus(int, Enum):
    Idle = 0
    Shipped = 1
    Finished = 2


class OrderBase(BaseModel):
    uid: str
    cid: str
    aid: str
    count: int


class Order(OrderBase):
    oid: str
    time: datetime
    status: OrderStatus
