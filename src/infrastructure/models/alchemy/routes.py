from sqlalchemy import String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from domain.entities.enums import PlaceCategory, PlaceType
from infrastructure.models.alchemy.base import Base
from infrastructure.models.alchemy.users import User


class Place(Base):
    __tablename__ = "places"

    name: Mapped[str] = mapped_column(String, index=True)
    category: Mapped[PlaceCategory] = mapped_column(
        Enum(PlaceCategory, name="place_category", native_enum=False), nullable=False
    )
    type: Mapped[PlaceType | None] = mapped_column(
        Enum(PlaceType, name="place_type", native_enum=False),
        default=None,
        server_default=None,
    )
    tags: Mapped[str | None] = mapped_column(default=None, server_default=None)
    coordinates: Mapped[str | None] = mapped_column(default=None, server_default=None)
    photo: Mapped[str | None] = mapped_column(default=None, server_default=None)
    map_name: Mapped[str | None] = mapped_column(default=None, server_default=None)

    route_places: Mapped[list["RoutePlace"]] = relationship(
        "RoutePlace", back_populates="place"
    )


class Route(Base):
    __tablename__ = "routes"

    name: Mapped[str] = mapped_column(String, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, server_default="now()"
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now, server_default="now()"
    )
    duration: Mapped[int | None] = mapped_column(default=None, server_default=None)
    distance: Mapped[int | None] = mapped_column(default=None, server_default=None)

    author: Mapped["User"] = relationship("User", back_populates="routes")
    places: Mapped[list["RoutePlace"]] = relationship(
        "RoutePlace", back_populates="route", cascade="all, delete-orphan"
    )
    likes: Mapped[list["Like"]] = relationship(
        "Like", back_populates="route", cascade="all, delete-orphan"
    )
    comments: Mapped[list["RouteComment"]] = relationship(
        "RouteComment", back_populates="route", cascade="all, delete-orphan"
    )


class RoutePlace(Base):
    __tablename__ = "route_places"

    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id"))
    order: Mapped[int]

    route: Mapped["Route"] = relationship("Route", back_populates="places")
    place: Mapped["Place"] = relationship("Place", back_populates="route_places")


class Like(Base):
    __tablename__ = "likes"

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    author: Mapped["User"] = relationship("User", back_populates="likes")
    route: Mapped["Route"] = relationship("Route", back_populates="likes")


class RouteComment(Base):
    __tablename__ = "route_comments"

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id", ondelete="CASCADE"))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    comment: Mapped[str | None] = mapped_column(default=None, server_default=None)
    photo: Mapped[str | None] = mapped_column(default=None, server_default=None)

    author: Mapped["User"] = relationship("User", back_populates="comments")
    route: Mapped["Route"] = relationship("Route", back_populates="comments")
