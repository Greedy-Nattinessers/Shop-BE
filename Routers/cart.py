import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from Models.commodity import CartCommodity
from Models.database import CartDb, CommodityDb
from Models.response import BaseResponse, ExceptionResponseEnum, StandardResponse
from Models.user import User
from Services.Database.database import get_db
from Services.Security.user import get_current_user

cart_router = APIRouter(prefix="/cart")
logger = logging.getLogger("cart")


@cart_router.post("/add", response_model=BaseResponse)
async def cart_add(
    cid: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    if db.query(CommodityDb).filter(CommodityDb.cid == cid).first() is None:
        raise ExceptionResponseEnum.NOT_FOUND()
    if (
        record := db.query(CartDb)
        .filter(CartDb.cid == cid.hex and CartDb.uid == user.uid)
        .first()
    ) is not None:
        record.count += 1
    else:
        db.add(CartDb(rid=uuid4().hex, cid=cid.hex, uid=user.uid, count=1))
    db.commit()
    return StandardResponse[None](status_code=200, message="Commodity added")


@cart_router.delete("/remove", response_model=BaseResponse)
async def cart_delete(
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


@cart_router.get("/all", response_model=BaseResponse[list[CartCommodity]])
async def cart_all(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[list[CartCommodity]]:
    data = db.query(CartDb).filter(CartDb.uid == user.uid).all()
    if not data:
        return StandardResponse[list[CartCommodity]](
            status_code=200, message=None, data=[]
        )

    commodities_data = (
        db.query(CommodityDb)
        .filter(CommodityDb.cid.in_([item.cid for item in data]))
        .all()
    )
    commodities_dict = {commodity.cid: commodity for commodity in commodities_data}

    commodities = []
    for item in data:
        commodity = commodities_dict.get(item.cid)
        if commodity is None:
            logger.warning(f"Commodity {item.cid} not found")
            continue
        commodities.append(
            CartCommodity(
                cid=commodity.cid,
                name=commodity.name,
                price=commodity.price,
                count=item.count,
                album=commodity.images[0] if commodity.images else None,
            )
        )

    return StandardResponse[list[CartCommodity]](
        status_code=200, message=None, data=commodities
    )
