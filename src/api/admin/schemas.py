from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from domain.entities.enums import CityCategory, PlaceCategory, PlaceType
from domain.filters import BaseFilter


class PlaceBase(BaseModel):
    name: str
    category: PlaceCategory
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[str] = None
    photo: Optional[str] = None
    map_name: Optional[str] = None


class PlaceCreate(BaseModel):
    name: str
    category: PlaceCategory
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[str] = None
    photo: Optional[str] = None
    map_name: Optional[str] = None


class PlacePut(BaseModel):
    name: str
    category: PlaceCategory
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[str] = None
    map_name: Optional[str] = None


class PlacePatch(BaseModel):
    name: str
    category: PlaceCategory
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[str] = None
    map_name: Optional[str] = None


class PlaceRead(BaseModel):
    id: int
    name: str
    category: PlaceCategory
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[str] = None
    photo: Optional[str] = None
    map_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True, use_enum_values=False)


class PlaceFilter(BaseFilter):
    name: Optional[str] = Field(None, description="Partial match for name")
    city: Optional[CityCategory] = None
    category: Optional[PlaceCategory] = None
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[str] = None
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


class PlaceSchema(BaseModel):
    id: int
    name: str
    category: str
    type: Optional[str]
    city: str
    coordinates: Optional[str]
    map_name: Optional[str]
    order: int
    photos: List[PhotoSchema] = []


class RouteSchema(BaseModel):
    id: int
    name: str
    author: AuthorSchema
    duration: Optional[int]
    distance: Optional[int]
    created_at: datetime
    updated_at: datetime
    photos: List[PhotoSchema] = []
    places: List[PlaceSchema] = []


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
    places: List[PlaceSchema] = []
