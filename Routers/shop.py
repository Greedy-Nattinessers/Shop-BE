import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from Models.commodity import Commodity, CreateCommodity
from Models.database import CommodityDb
from Models.response import ExceptionResponse, StandardResponse
from Models.user import Permission, User
from Services.Database.database import get_db
from Services.Limiter.limiter import limiter
from Services.Security.user import get_current_user, verify_user

shop_router = APIRouter(prefix="/shop")
logger = logging.getLogger("shop")


@shop_router.post("/add", response_model=StandardResponse)
async def add_commodity(
    body: CreateCommodity,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse:
    assert verify_user(user, Permission.Admin)

    db.add(CommodityDb(**body.to_commodity().model_dump()))
    db.commit()

    return StandardResponse(status_code=201, message="Commodity added")


@shop_router.get("/all", response_model=StandardResponse)
@limiter.limit("10/minute")
async def all_commodity(
    request: Request, page: int = 1, db: Session = Depends(get_db)
) -> StandardResponse[list[Commodity]]:
    commodities = [
        Commodity(
            cid=item.cid, name=item.name, price=item.price, description=item.description
        )
        for item in db.query(CommodityDb).offset((page - 1) * 50).limit(50).all()
    ]

    return StandardResponse[list[Commodity]](
        status_code=200, message="Commodities", data=commodities
    )


@shop_router.put("/update", response_model=StandardResponse)
async def edit_commodity(
    body: Commodity,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse:
    assert verify_user(user, Permission.Admin)

    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == body.cid).first()
    ) is not None:
        record.name = body.name
        record.price = body.price
        record.description = body.description
        db.commit()
        return StandardResponse(status_code=200, message="Commodity updated")
    else:
        raise ExceptionResponse.NOT_FOUND


@shop_router.delete("/delete", response_model=StandardResponse)
async def remove_commodity(
    cid: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> StandardResponse:
    assert verify_user(user, Permission.Admin)
    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == cid).first()
    ) is not None:
        db.delete(record)
        db.commit()
        return StandardResponse(status_code=200, message="Commodity deleted")
    else:
        raise ExceptionResponse.NOT_FOUND
