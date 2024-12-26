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


@cart_router.post("/add/{cid}", response_model=BaseResponse)
def add_cart(
    cid: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    if db.query(CommodityDb).filter(CommodityDb.cid == cid).first() is None:
        raise ExceptionResponseEnum.NOT_FOUND()
    if (
        record := db.query(CartDb)
        .filter(CartDb.cid == cid.hex, CartDb.uid == user.uid)
        .first()
    ) is not None:
        record.count += 1
    else:
        db.add(CartDb(rid=uuid4().hex, cid=cid.hex, uid=user.uid, count=1))
    db.commit()
    return StandardResponse[None](message="Commodity added")


@cart_router.delete("/remove/{cid}", response_model=BaseResponse)
def remove_cart(
    cid: UUID,
    remove_all: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    if (
        record := db.query(CartDb)
        .filter(CartDb.cid == cid.hex, CartDb.uid == user.uid)
        .first()
    ) is None:
        raise ExceptionResponseEnum.NOT_FOUND()
    if remove_all or record.count <= 1:
        db.query(CartDb).filter(CartDb.cid == cid.hex, CartDb.uid == user.uid).delete()
    else:
        record.count -= 1
    db.commit()
    return StandardResponse[None](message="Commodity deleted")


@cart_router.delete("/all", response_model=BaseResponse)
def clear_cart(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> StandardResponse[None]:
    record = db.query(CartDb).filter(CartDb.uid == user.uid)
    if len(record.all()) == 0:
        return StandardResponse[None](message="Cart is empty")
    record.delete()
    db.commit()
    return StandardResponse[None](message="Cart cleared")


@cart_router.get("/all", response_model=BaseResponse[list[CartCommodity]])
def all_cart(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[list[CartCommodity]]:
    data = db.query(CartDb).filter(CartDb.uid == user.uid).all()
    if not data:
        return StandardResponse[list[CartCommodity]](message=None, data=[])

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

    return StandardResponse[list[CartCommodity]](message=None, data=commodities)
