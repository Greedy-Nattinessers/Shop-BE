import logging

from typing import List
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from Models.cart import cartProduct,cartRecord
from Models.commodity import Commodity
from Models.database import CartDb,CommodityDb
from Models.response import ExceptionResponse, StandardResponse
from Models.user import Permission, User
from Services.Database.database import get_db
from Services.Limiter.limiter import limiter
from Services.Security.user import get_current_user, verify_user

cart_router = APIRouter(prefix="/cart")
logger = logging.getLogger("cart")

@cart_router.post("/add")
async def addToCart(
    product: cartProduct,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
)->StandardResponse:
    db.add(CartDb(cartRecord(product.id,user.uid)))
    db.commit()
    return StandardResponse(status_code=201,message="added to cart")


@cart_router.post("/delete")
async def deleteFromCart(
     product: cartProduct,
     user:User = Depends(get_current_user),
     db: Session = Depends(get_db)

)->StandardResponse:
     
    if ( 
      record := db.query(CartDb).filter(CartDb.productId == product.id and CartDb.userUid == user.uid).first()
    ) is not None:
        db.delete(record)
        db.commit()
        return StandardResponse(status_code=20, message="good delete")
    else:
        raise ExceptionResponse.NOT_FOUND

#todo
@cart_router.get("/query")
async def getCartList(
    page: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
)->StandardResponse[List[Commodity]]:
    commodities = [
        Commodity(
            cid=item.cid, name=item.name, price=item.price, description=item.description
        )
        for item in db.query(CartDb).filter(CartDb.userUid == user.uid).\
            join(Commodity, CartDb.productId == Commodity.cid).\
            offset((page-1) * 10).limit(10)
    ]
    return StandardResponse[List[Commodity]](status_code=200,message='page'+ str(page),data =commodities )

