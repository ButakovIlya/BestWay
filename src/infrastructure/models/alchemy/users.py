from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.enums import Gender
from infrastructure.models.alchemy.base import Base

if TYPE_CHECKING:
    from infrastructure.models.alchemy.posts import Post
    from infrastructure.models.alchemy.routes import Comment, Like, Photo, Route
    from infrastructure.models.alchemy.surveys import Survey


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    phone: Mapped[str] = mapped_column(String, unique=True, index=True)
    first_name: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    middle_name: Mapped[str | None] = mapped_column(String, index=True, nullable=True)
    registration_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    photo: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    gender: Mapped[str] = mapped_column(
        Enum(Gender, name="user_gender", native_enum=False, length=16),
        index=True,
        default=Gender.MALE,
    )
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    routes: Mapped[list["Route"]] = relationship("Route", back_populates="author")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="author")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="author")
    uploaded_photos: Mapped[list["Photo"]] = relationship("Photo", back_populates="uploader")
    surveys: Mapped[list["Survey"]] = relationship(
        "Survey", back_populates="author", cascade="all, delete-orphan", lazy="selectin"
    )
    posts: Mapped[list["Post"]] = relationship(
        "Post", back_populates="author", cascade="all, delete-orphan"
    )
