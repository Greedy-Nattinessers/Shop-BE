from sqlalchemy import DECIMAL, INT, JSON, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from Services.Config.config import config
from Services.Database.database import Base, engine


class UserDb(Base):
    __tablename__ = "user"
    uid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    username: Mapped[str] = mapped_column(TEXT, nullable=False)
    email: Mapped[str] = mapped_column(TEXT, nullable=False)
    password: Mapped[str] = mapped_column(TEXT, nullable=False)
    permission: Mapped[int] = mapped_column(INT, nullable=False)


class CommodityDb(Base):
    __tablename__ = "commodity"
    cid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(TEXT, nullable=True)
    images: Mapped[list[str]] = mapped_column(JSON, nullable=False)


class AddressDb(Base):
    __tablename__ = "address"
    aid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    uid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    address: Mapped[str] = mapped_column(TEXT, nullable=False)
    phone: Mapped[str] = mapped_column(TEXT, nullable=False)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    is_default: Mapped[bool] = mapped_column(INT, nullable=False)


class CartDb(Base):
    __tablename__ = "cart"
    rid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    uid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    cid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    count: Mapped[int] = mapped_column(INT, nullable=False)


if config.test is not None and config.test.is_test:
    Base.metadata.drop_all(engine)
Base.metadata.create_all(engine, checkfirst=True)
