from datetime import datetime
from tokenize import Comment
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.models.alchemy.base import Base

if TYPE_CHECKING:
    from infrastructure.models.alchemy.routes import Comment, Like, Route
    from infrastructure.models.alchemy.users import User


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(Text, default=None, server_default=None)
    photo: Mapped[str | None] = mapped_column(String, default=None, server_default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, server_default="now()"
    )

    route: Mapped["Route"] = relationship("Route", back_populates="posts", lazy="selectin")
    author: Mapped["User"] = relationship("User", back_populates="posts", lazy="selectin")
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")  # type: ignore
