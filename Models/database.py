from sqlalchemy import VARCHAR, Text
from sqlalchemy.orm import Mapped, mapped_column

from Models import user
from Services.Database.database import Base


class UserDb(Base):
    __tablename__ = "user"
    uid: Mapped[str] = mapped_column(
        __name_pos=VARCHAR(32),
        primary_key=True,
        nullable=False,
        unique=True,
        index=True,
    )
    username: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(Text, nullable=False)
