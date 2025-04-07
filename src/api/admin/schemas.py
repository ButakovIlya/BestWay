from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from domain.entities.enums import CityCategory, PlaceCategory, PlaceType
from domain.filters import BaseFilter
from infrastructure.models.alchemy.routes import Photo, Place


class CommonPlaceBase(BaseModel):
    name: str
    category: PlaceCategory
    city: Optional[CityCategory] = None
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[List[float]] = None
    map_name: Optional[str] = None

    @field_validator("coordinates")
    def validate_coordinates(cls, value):
        if value is None:
            return value
        if isinstance(value, list) and len(value) == 2 and all(isinstance(x, (float, int)) for x in value):
            return [float(x) for x in value]
        raise ValueError("coordinates must be a list of two float values or None")


class PlaceCreate(CommonPlaceBase):
    pass


class PlacePut(CommonPlaceBase):
    name: str
    category: PlaceCategory
    city: CityCategory = None
    type: PlaceType = None
    tags: str = None
    coordinates: List[float] = None
    map_name: str = None


class PlacePatch(CommonPlaceBase):
    name: Optional[str] = None
    category: Optional["PlaceCategory"] = None


class PhotoRead(BaseModel):
    id: int
    url: str

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, photo: Any) -> "PhotoRead":
        url = getattr(photo, "url", None) or photo.get("url")
        id_ = getattr(photo, "id", None) or photo.get("id")

        return cls(
            id=id_,
            url=f"http://localhost:8002/{url.lstrip('/')}" if url else "",
        )


class PlaceRead(CommonPlaceBase):
    id: int
    photo: Optional[str] = None
    photos: Optional[List[PhotoRead]] = None

    model_config = {"from_attributes": True, "use_enum_values": False}

    @classmethod
    def model_validate(cls, place: Place) -> "PlaceRead":
        return cls(
            id=place.id,
            name=place.name,
            city=place.city,
            category=place.category,
            type=place.type,
            tags=place.tags,
            coordinates=place.coordinates,
            photo=place.photo,
            map_name=place.map_name,
            photos=[PhotoRead.model_validate(photo) for photo in place.photos] if place.photos else None,
        )


class PlaceFilter(BaseFilter):
    name: Optional[str] = Field(None, description="Partial match for name")
    city: Optional[CityCategory] = None
    category: Optional[PlaceCategory] = None
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[list] = None
    map_name: Optional[str] = None

    name__list: Optional[List[str]] = None
    city__list: Optional[List[CityCategory]] = None
    type__list: Optional[List[PlaceType]] = None
    category__list: Optional[List[PlaceCategory]] = None


class PhotoSchema(BaseModel):
    url: str


class AuthorSchema(BaseModel):
    id: int
    first_name: str
    last_name: str


class RouteSchema(BaseModel):
    id: int
    name: str
    author: AuthorSchema
    duration: Optional[int]
    distance: Optional[int]
    created_at: datetime
    updated_at: datetime
    photos: List[PhotoSchema] = []
    places: List[PlaceRead] = []


class RoutePutSchema(BaseModel):
    id: int
    name: str
    author: int
    duration: int
    distance: int


class RoutePatchSchema(BaseModel):
    id: int
    name: str | None = None
    author: int | None = None
    duration: Optional[int] = None
    distance: Optional[int] = None


class RouteCreateSchema(BaseModel):
    id: int
    name: str
    author: AuthorSchema
    duration: Optional[int]
    distance: Optional[int]
    created_at: datetime
    updated_at: datetime
    photos: List[PhotoSchema] = []
    places: List[PlaceRead] = []
