from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.entities.enums import CityCategory, PlaceCategory, PlaceType, RouteType
from infrastructure.models.alchemy.base import Base

if TYPE_CHECKING:
    from infrastructure.models.alchemy.users import User


class Place(Base):
    __tablename__ = "places"

    name: Mapped[str] = mapped_column(String, index=True)
    city: Mapped[str] = mapped_column(
        Enum(CityCategory, name="place_category", native_enum=False, length=16),
        index=True,
        default=CityCategory.PERM,
    )
    category: Mapped[PlaceCategory] = mapped_column(
        Enum(PlaceCategory, name="place_category", native_enum=False), nullable=False
    )
    type: Mapped[PlaceType | None] = mapped_column(
        Enum(PlaceType, name="place_type", native_enum=False),
        default=None,
        server_default=None,
    )
    tags: Mapped[str | None] = mapped_column(default=None, server_default=None)
    coordinates: Mapped[list | None] = mapped_column(JSON, default=None, server_default=None)
    photo: Mapped[str | None] = mapped_column(default=None, server_default=None)
    map_name: Mapped[str | None] = mapped_column(default=None, server_default=None)
    json_data: Mapped[dict | None] = mapped_column(JSON, default=None, server_default=None)

    route_places: Mapped[list["RoutePlace"]] = relationship(
        "RoutePlace", back_populates="place", lazy="selectin"
    )
    photos: Mapped[list["Photo"]] = relationship(
        "Photo", back_populates="place", cascade="all, delete-orphan", lazy="selectin"
    )
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="place", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="place", cascade="all, delete-orphan"
    )


class Route(Base):
    __tablename__ = "routes"

    name: Mapped[str] = mapped_column(String, index=True)
    type: Mapped[RouteType] = mapped_column(
        Enum(RouteType, name="route_type", native_enum=False),
        default=RouteType.MIXED,
    )
    city: Mapped[str] = mapped_column(
        Enum(CityCategory, name="route_city", native_enum=False, length=16),
        index=True,
        default=CityCategory.PERM,
    )
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    duration: Mapped[int | None] = mapped_column(default=None, server_default=None)
    distance: Mapped[int | None] = mapped_column(default=None, server_default=None)
    is_custom: Mapped[bool] = mapped_column(default=False, server_default="false")

    photo: Mapped[str | None] = mapped_column(default=None, server_default=None)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, server_default="now()"
    )
    json_data: Mapped[dict | None] = mapped_column(JSON, default=None, server_default=None)

    author: Mapped["User"] = relationship("User", back_populates="routes")
    places: Mapped[list["RoutePlace"]] = relationship(
        "RoutePlace", back_populates="route", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship("Like", back_populates="route", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="route", cascade="all, delete-orphan"
    )
    photos: Mapped[list["Photo"]] = relationship(
        "Photo", back_populates="route", cascade="all, delete-orphan"
    )


class RoutePlace(Base):
    __tablename__ = "route_places"

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"))
    order: Mapped[int] = mapped_column(default=0)

    route: Mapped["Route"] = relationship("Route", back_populates="places", lazy="selectin")
    place: Mapped["Place"] = relationship("Place", back_populates="route_places", lazy="selectin")


class Like(Base):
    __tablename__ = "likes"

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    author: Mapped["User"] = relationship("User", back_populates="likes", lazy="selectin")
    route: Mapped["Route"] = relationship("Route", back_populates="likes", lazy="selectin")
    place: Mapped["Place"] = relationship("Place", back_populates="likes", lazy="selectin")


class Comment(Base):
    __tablename__ = "route_comments"

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    comment: Mapped[str | None] = mapped_column(default=None, server_default=None)
    photo: Mapped[str | None] = mapped_column(default=None, server_default=None)

    author: Mapped["User"] = relationship("User", back_populates="comments", lazy="selectin")
    route: Mapped["Route"] = relationship("Route", back_populates="comments", lazy="selectin")
    place: Mapped["Place"] = relationship("Place", back_populates="comments", lazy="selectin")


class Photo(Base):
    __tablename__ = "photos"

    url: Mapped[str] = mapped_column(String, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, server_default="now()")
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    place_id: Mapped[int | None] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), nullable=True)
    route_id: Mapped[int | None] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"), nullable=True)

    place: Mapped["Place"] = relationship("Place", back_populates="photos", lazy="selectin")
    route: Mapped["Route"] = relationship("Route", back_populates="photos", lazy="selectin")
    uploader: Mapped["User"] = relationship("User", back_populates="uploaded_photos", lazy="selectin")
