from sqlalchemy import DECIMAL, INT, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from Services.Database.database import Base


class UserDb(Base):
    __tablename__ = "user"
    uid: Mapped[str] = mapped_column(
        VARCHAR(32),
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
    )
    username: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(TEXT, nullable=False)
    permission: Mapped[int] = mapped_column(INT, nullable=False)


class CommodityDb(Base):
    __tablename__ = "commodity"
    cid: Mapped[str] = mapped_column(
        VARCHAR(32),
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(TEXT)

class CartDb(Base):
    __tablename__ = "cart"
    userUid:Mapped[str] = mapped_column(TEXT, primary_key=True)
    productId: Mapped[str] = mapped_column(TEXT,primary_key=True)