import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.security import SecurityScopes
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


@shop_router.post("/add_commodity", response_model=StandardResponse)
@limiter.limit("5/minute")
async def add_commodity(
    commodity: CreateCommodity,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> StandardResponse:
    assert verify_user(user, Permission.Shop)

    db.add(CommodityDb(**commodity.to_commodity().model_dump()))
    db.commit()

    return StandardResponse(status_code=201, message="Commodity added")
