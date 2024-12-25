import asyncio
import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Form, Response, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from Models.commodity import (
    BaseCommodity,
    Comment,
    CommentBase,
    Commodity,
    CreateCommodity,
    UpdateCommodity,
)
from Models.database import CommentDb, CommodityDb
from Models.response import BaseResponse, ExceptionResponseEnum, StandardResponse
from Models.user import Permission, User
from Services.Database.database import get_db
from Services.Security.user import get_current_user, verify_user
from Services.Storage.manager import load_file_async, remove_file, save_file_async

shop_router = APIRouter(prefix="/shop")
logger = logging.getLogger("shop")


@shop_router.post("/add", response_model=BaseResponse[str], status_code=201)
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


@shop_router.get("/all", response_model=BaseResponse[list[BaseCommodity]])
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


@shop_router.get("/item/{commodity}", response_model=BaseResponse[Commodity])
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


@shop_router.get("/item/{commodity}/album", response_class=Response)
async def get_commodity_album(
    commodity: UUID, db: Session = Depends(get_db)
) -> Response:
    if (
        (
            record := db.query(CommodityDb)
            .filter(CommodityDb.cid == commodity.hex)
            .first()
        )
        is not None
        and (album := record.images[0] if record.images.__len__() > 0 else None)
        is not None
        and (data := await load_file_async(UUID(album))) is not None
    ):
        return Response(content=data[0], media_type=data[1])
    raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.get("/image/{fid}", response_class=Response)
async def get_commodity_image(fid: UUID) -> Response:
    if (data := await load_file_async(fid)) is not None:
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

        if no_images or images.__len__() > 0:
            for img in record.images:
                if not remove_file(UUID(img)):
                    logger.warning(f"Failed to remove image {img}, record {cid}")
            tasks = [save_file_async(await img.read()) for img in images]
            imgs_id = await asyncio.gather(*tasks)

            record.images = jsonable_encoder([img.hex for img in imgs_id])
        db.commit()
        return StandardResponse[None](status_code=200, message="Commodity updated")
    raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.delete("/item/{cid}", response_model=BaseResponse)
async def remove_commodity(
    cid: UUID, user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> StandardResponse[None]:
    assert verify_user(user, Permission.ADMIN)

    if (
        record := db.query(CommodityDb).filter(CommodityDb.cid == cid.hex).first()
    ) is not None:
        imgs = record.images
        db.delete(record)

        for comment in db.query(CommentDb).filter(CommentDb.commodity == cid.hex).all():
            db.delete(comment)

        db.commit()
        for img in imgs:
            if not remove_file(UUID(img)):
                logger.warning(f"Failed to remove image {img}, record {cid}")
        return StandardResponse[None](status_code=200, message="Commodity removed")

    else:
        raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.post("/item/{cid}/comment", response_model=BaseResponse, status_code=201)
async def add_comment(
    cid: UUID,
    body: CommentBase,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    if db.query(CommodityDb).filter(CommodityDb.cid == cid.hex).first() is not None:
        db.add(
            CommentDb(
                cid=uuid4().hex,
                uid=user.uid,
                commodity=cid.hex,
                content=body.content,
            )
        )
        db.commit()
        return StandardResponse[None](status_code=201, message="Comment added")
    raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.get("/item/{cid}/comment", response_model=BaseResponse[list[Comment]])
async def get_comment(
    cid: UUID,
    db: Session = Depends(get_db),
) -> StandardResponse[list[Comment]]:
    if db.query(CommodityDb).filter(CommodityDb.cid == cid.hex).first() is not None:
        comments = [
            Comment(**item.__dict__)
            for item in db.query(CommentDb).filter(CommentDb.commodity == cid.hex).all()
        ]

        return StandardResponse[list[Comment]](
            status_code=200, message=None, data=comments
        )
    raise ExceptionResponseEnum.NOT_FOUND()


@shop_router.delete("/comment/{id}", response_model=BaseResponse)
async def delete_comment(
    id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    if (
        record := db.query(CommentDb).filter(CommentDb.cid == id.hex).first()
    ) is not None:
        if record.uid != user.uid and not verify_user(user, Permission.ADMIN):
            raise ExceptionResponseEnum.PERMISSION_DENIED()
        db.delete(record)
        db.commit()
        return StandardResponse[None](status_code=200, message="Comment removed")
    raise ExceptionResponseEnum.NOT_FOUND()
