from sqlalchemy import DECIMAL, INT, TEXT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from Services.Database.database import Base


class UserDb(Base):
    __tablename__ = "user"
    uid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    username: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(TEXT, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(TEXT, nullable=False)
    permission: Mapped[int] = mapped_column(INT, nullable=False)


class CommodityDb(Base):
    __tablename__ = "commodity"
    cid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False)
    description: Mapped[str] = mapped_column(TEXT, nullable=True)
    image: Mapped[str] = mapped_column(VARCHAR(32), nullable=True)


class AddressDb(Base):
    __tablename__ = "address"
    aid: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    uid: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    address: Mapped[str] = mapped_column(TEXT, nullable=False)
    phone: Mapped[str] = mapped_column(TEXT, nullable=False)
    name: Mapped[str] = mapped_column(TEXT, nullable=False)
    is_default: Mapped[bool] = mapped_column(INT, nullable=False)