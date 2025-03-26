# schemas/place.py
from pydantic import BaseModel
from typing import Optional

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

class PlaceUpdate(BaseModel):
    pass

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
        orm_mode = True
