import asyncio
import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Form, Response, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from Models.commodity import BaseCommodity, Commodity, CreateCommodity, UpdateCommodity
from Models.database import CommodityDb
from Models.response import BaseResponse, ExceptionResponseEnum, StandardResponse
from Models.user import Permission, User
from Services.Database.database import get_db
from Services.Security.user import get_current_user, verify_user
from Services.Storage.manager import load_file_async, remove_file, save_file_async

shop_router = APIRouter(prefix="/shop")
logger = logging.getLogger("shop")


@shop_router.post("/add", response_model=BaseResponse)
async def add_commodity(
    body: CreateCommodity = Form(),
    images: list[UploadFile] = [],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[str]:
    assert verify_user(user, Permission.ADMIN)
    if images.__len__() > 5:
        raise ExceptionResponseEnum.INVALID_OPERATION()

    cid = uuid4()

    tasks = [save_file_async(await img.read()) for img in images]
    imgs_id = await asyncio.gather(*tasks)

    db.add(
        CommodityDb(
            cid=cid.hex,
            name=body.name,
            price=body.price,
            images=jsonable_encoder([img.hex for img in imgs_id]),
            description=body.description,
        )
    )
    db.commit()

    return StandardResponse[str](
        status_code=201, message="Commodity added", data=cid.hex
    )


@shop_router.get("/all", response_model=BaseResponse)
async def all_commodity(
    page: int = 1, db: Session = Depends(get_db)
) -> StandardResponse[list[BaseCommodity]]:
    if page < 1:
        raise ExceptionResponseEnum.INVALID_OPERATION()

    commodities = [
        BaseCommodity(
            cid=item.cid,
            name=item.name,
            price=item.price,
            album=item.images[0] if item.images.__len__() > 0 else None,
        )
        for item in db.query(CommodityDb).offset((page - 1) * 50).limit(50).all()
    ]

    return StandardResponse[list[BaseCommodity]](
        status_code=200, message=None, data=commodities
    )


@shop_router.get("/item/{commodity}", response_model=BaseResponse)
async def get_commodity(
    commodity: UUID, db: Session = Depends(get_db)
) -> StandardResponse[Commodity]:
    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == commodity.hex).first()
    ) is not None:
        return StandardResponse[Commodity](
            status_code=200,
            message=None,
            data=Commodity(
                cid=record.cid,
                name=record.name,
                price=record.price,
                description=record.description,
                images=record.images,
                album=record.images[0] if record.images.__len__() > 0 else None,
            ),
        )
    raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.get("/image/{cid}", response_class=Response)
async def get_commodity_image(cid: UUID) -> Response:
    if (data := await load_file_async(cid.hex)) is not None:
        return Response(content=data[0], media_type=data[1])

    raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.put("/item/{cid}", response_model=BaseResponse)
async def edit_commodity(
    cid: UUID,
    no_images: bool = False,
    body: UpdateCommodity = Form(),
    images: list[UploadFile] = [],
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    assert verify_user(user, Permission.ADMIN)

    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == cid.hex).first()
    ) is not None:
        if body.name is not None:
            record.name = body.name
        if body.price is not None:
            record.price = body.price
        if body.description is not None:
            record.description = body.description
        if images.__len__() > 5:
            raise ExceptionResponseEnum.INVALID_OPERATION()

        tasks = [save_file_async(await img.read()) for img in images]
        imgs_id = await asyncio.gather(*tasks)

        record.images = jsonable_encoder([img.hex for img in imgs_id])
        db.commit()
        return StandardResponse[None](status_code=200, message="Commodity updated")
    raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.put("/image/{cid}", response_model=BaseResponse)
async def edit_commodity_image(
    cid: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    assert verify_user(user, Permission.ADMIN)

    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == cid.hex).first()
    ) is not None:

        db.commit()
        return StandardResponse[None](status_code=200, message="Commodity updated")
    raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.delete("/delete/{cid}", response_model=BaseResponse)
async def remove_commodity(
    cid: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> StandardResponse[None]:
    assert verify_user(user, Permission.ADMIN)

    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == cid.hex).first()
    ) is not None:
        imgs = record.images
        db.delete(record)
        db.commit()
        for img in imgs:
            if not remove_file(UUID(img)):
                logger.warning(f"Failed to remove image {img}, record {cid}")
        return StandardResponse[None](status_code=200, message="Commodity removed")

    else:
        raise ExceptionResponseEnum.NOT_FOUND()
