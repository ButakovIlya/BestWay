from typing import Optional

from pydantic import BaseModel

from domain.entities.enums import PlaceCategory, PlaceType


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

    class Config:
        from_attributes = True
