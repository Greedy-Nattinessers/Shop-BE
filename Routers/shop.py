import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, Request, Response, UploadFile
from sqlalchemy.orm import Session

from Models.commodity import Commodity, CreateCommodity
from Models.database import CommodityDb
from Models.response import BaseResponse, ExceptionResponseEnum, StandardResponse
from Models.user import Permission, User
from Services.Database.database import get_db
from Services.Limiter.slow_limiter import freq_limiter
from Services.Security.user import get_current_user, verify_user
from Services.Storage.manager import load_file_async, remove_file, save_file_async

shop_router = APIRouter(prefix="/shop")
logger = logging.getLogger("shop")


@shop_router.post("/add", response_model=BaseResponse)
async def add_commodity(
    body: CreateCommodity = Form(),
    img: UploadFile | None = None,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    assert verify_user(user, Permission.Admin)

    fid = None
    cid = uuid4().hex
    if img is not None:
        contents = await img.read()
        fid = await save_file_async(contents, cid)

    db.add(CommodityDb(**body.to_commodity(cid, fid).model_dump()))
    db.commit()

    return StandardResponse[None](status_code=201, message="Commodity added")


@shop_router.get("/all", response_model=BaseResponse)
@freq_limiter.limit("10/minute")
async def all_commodity(
    request: Request, page: int = 1, db: Session = Depends(get_db)
) -> StandardResponse[list[Commodity]]:
    if page < 1:
        raise ExceptionResponseEnum.INVALID_OPERATION()

    commodities = [
        Commodity(**item.__dict__)
        for item in db.query(CommodityDb).offset((page - 1) * 50).limit(50).all()
    ]

    return StandardResponse[list[Commodity]](
        status_code=200, message=None, data=commodities
    )


@shop_router.get("/image", response_class=Response)
async def get_commodity_image(cid: str):
    if (data := await load_file_async(cid)) is not None:
        return Response(content=data[0], media_type=data[1])


@shop_router.put("/update", response_model=BaseResponse)
async def edit_commodity(
    body: Commodity,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    assert verify_user(user, Permission.Admin)

    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == body.cid).first()
    ) is not None:
        record.name = body.name
        record.price = body.price
        record.description = body.description
        db.commit()
        return StandardResponse[None](status_code=200, message="Commodity updated")
    else:
        raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.delete("/delete", response_model=BaseResponse)
async def remove_commodity(
    cid: str, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> StandardResponse[None]:
    assert verify_user(user, Permission.Admin)
    
    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == cid).first()
    ) is not None:
        db.delete(record)
        db.commit()
        remove_file(cid)
        return StandardResponse[None](status_code=200, message="Commodity deleted")
    else:
        raise ExceptionResponseEnum.NOT_FOUND()
