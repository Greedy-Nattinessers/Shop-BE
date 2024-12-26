import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from Models.database import CommodityDb, OrderDb
from Models.order import Order, OrderBase, OrderStatus
from Models.response import BaseResponse, ExceptionResponseEnum, StandardResponse
from Models.user import Permission, User
from Services.Database.database import get_db
from Services.Limiter.slow_limiter import freq_limiter
from Services.Security.user import get_current_user, verify_user

order_router = APIRouter(prefix="/order")
logger = logging.getLogger("order")


@order_router.post("/add", response_model=BaseResponse[str], status_code=201)
@freq_limiter.limit("10/minute")
def add_order(
    request: Request,
    body: OrderBase,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[str]:
    if body.content.__len__() < 1:
        raise ExceptionResponseEnum.INVALID_OPERATION()

    for cid, count in body.content.items():
        if count < 1:
            raise ExceptionResponseEnum.INVALID_OPERATION()
        if db.query(CommodityDb).filter(CommodityDb.cid == cid).first() is None:
            raise ExceptionResponseEnum.NOT_FOUND()

    oid = uuid4().hex
    db.add(
        OrderDb(
            oid=oid,
            uid=user.uid,
            aid=body.aid,
            content=body.content,
            status=OrderStatus.Idle.value,
        )
    )
    db.commit()

    return StandardResponse[str](status_code=201, message="Order created", data=oid)


@order_router.get("/list", response_model=BaseResponse[list[Order]])
def all_order(
    page: int = 1, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> StandardResponse[list[Order]]:
    if page < 1:
        raise ExceptionResponseEnum.INVALID_OPERATION()

    record = (
        db.query(OrderDb)
        .filter(OrderDb.uid == user.uid)
        .offset((page - 1) * 10)
        .limit(10)
        .all()
    )
    return StandardResponse[list[Order]](
        data=[
            Order(
                oid=item.oid,
                uid=item.uid,
                aid=item.aid,
                content=item.content,
                time=item.time,
                status=OrderStatus(item.status),
            )
            for item in record
        ]
    )


@order_router.put("/{oid}/cancel", response_model=BaseResponse)
def cancel_order(
    oid: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    if (record := db.query(OrderDb).filter(OrderDb.oid == oid).first()) is None:
        raise ExceptionResponseEnum.NOT_FOUND()

    if record.uid != user.uid or record.status != OrderStatus.Idle.value:
        raise ExceptionResponseEnum.INVALID_OPERATION()

    record.status = OrderStatus.Canceled.value
    db.commit()

    return StandardResponse[None](message="Order canceled")


@order_router.put("/{oid}", response_model=BaseResponse)
def update_order_status(
    oid: str,
    status: OrderStatus,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    assert verify_user(user, Permission.ADMIN)

    if (record := db.query(OrderDb).filter(OrderDb.oid == oid).first()) is None:
        raise ExceptionResponseEnum.NOT_FOUND()

    record.status = status.value
    db.commit()

    return StandardResponse[None](message="Order status updated")
