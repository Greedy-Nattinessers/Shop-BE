import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Models.database import CartDb, CommodityDb
from Models.response import ExceptionResponseEnum, StandardResponse
from Models.user import User
from Services.Database.database import get_db
from Services.Security.user import get_current_user

cart_router = APIRouter(prefix="/cart")
logger = logging.getLogger("cart")


@cart_router.post("/add")
async def addToCart(
    cid: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse:
    if db.query(CommodityDb).filter(CommodityDb.cid == cid).first() is None:
        raise ExceptionResponseEnum.NOT_FOUND()
    if (
        record := db.query(CartDb)
        .filter(CartDb.cid == cid.hex and CartDb.uid == user.uid)
        .first()
    ) is not None:
        record.count += 1
    else:
        db.add(CartDb(cid=cid.hex, uid=user.uid, count=1))
    db.commit()
    return StandardResponse[None](status_code=200, message="Commodity added")


@cart_router.delete("/remove")
async def deleteFromCart(
    cid: UUID,
    is_all: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:

    if (
        record := db.query(CartDb)
        .filter(CartDb.cid == cid.hex and CartDb.uid == user.uid)
        .first()
    ) is None:
        raise ExceptionResponseEnum.NOT_FOUND()
    if is_all or record.count <= 1:
        db.query(CartDb).filter(
            CartDb.cid == cid.hex and CartDb.uid == user.uid
        ).delete()
    else:
        record.count -= 1
    db.commit()
    return StandardResponse[None](status_code=200, message="Commodity deleted")
