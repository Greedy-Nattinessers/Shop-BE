from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column

from Models import user
from Services.Database.database import Base


class UserDb(Base):
    __tablename__ = "user"
    uid: Mapped[str] = mapped_column(
        Text, primary_key=True, nullable=False, unique=True, index=True
    )
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)

class UserCartDb(Base):
    __tablename__ = "UserCart"
    userUid:Mapped[str] = mapped_column(Text, primary_key=True)
    productId: Mapped[str] = mapped_column(Text,primary_key=True)

