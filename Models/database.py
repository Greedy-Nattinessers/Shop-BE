from datetime import date, datetime

from sqlalchemy import DATE, DATETIME, DECIMAL, INT, JSON, TEXT, VARCHAR
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
    birthday: Mapped[date | None] = mapped_column(DATE, nullable=True)
    gender: Mapped[int] = mapped_column(INT, nullable=False)
    aid: Mapped[str | None] = mapped_column(VARCHAR(32), nullable=True)


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


class CartDb(Base):
    __tablename__ = "cart"
    rid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    uid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    cid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    count: Mapped[int] = mapped_column(INT, nullable=False)


class CommentDb(Base):
    __tablename__ = "comment"
    cid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    uid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    commodity: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True), default=datetime.now()
    )


class OrderDb(Base):
    __tablename__ = "order"
    oid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    uid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    aid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    content: Mapped[dict[str, int]] = mapped_column(JSON, nullable=False)
    time: Mapped[datetime] = mapped_column(
        DATETIME(timezone=True), default=datetime.now()
    )
    status: Mapped[int] = mapped_column(INT, nullable=False)


if config.test is not None and config.test.is_test:
    Base.metadata.drop_all(engine)
Base.metadata.create_all(engine, checkfirst=True)
