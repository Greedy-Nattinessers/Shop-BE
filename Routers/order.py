import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from Models.database import OrderDb
from Models.order import OrderBase, OrderStatus
from Models.response import BaseResponse, StandardResponse
from Models.user import User
from Services.Database.database import get_db
from Services.Limiter.slow_limiter import freq_limiter
from Services.Security.user import get_current_user

cart_router = APIRouter(prefix="/order")
logger = logging.getLogger("order")


@cart_router.post("/add", response_model=BaseResponse[str], status_code=201)
@freq_limiter.limit("10/minute")
def order_add(
    request: Request,
    body: OrderBase,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[str]:
    oid = uuid4().hex
    db.add(
        OrderDb(
            oid=oid,
            uid=user.uid,
            cid=body.cid,
            aid=body.aid,
            count=body.count,
            status=OrderStatus.Idle.value,
        )
    )

    return StandardResponse[str](status_code=201, data=oid)
