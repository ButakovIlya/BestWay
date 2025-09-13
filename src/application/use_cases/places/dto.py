from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from application.use_cases.common.dto import ModelPhotoDTO
from domain.entities.enums import CityCategory, PlaceCategory, PlaceType


class PlaceDTO(BaseModel):
    id: int
    city: CityCategory
    name: str
    description: Optional[str]
    website_url: Optional[str]
    category: PlaceCategory
    type: Optional[PlaceType]
    tags: Optional[str]
    coordinates: Optional[List[float]]
    photo: Optional[str]
    map_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CreatePlaceDTO(BaseModel):
    city: CityCategory
    name: str
    description: Optional[str]
    category: PlaceCategory
    type: Optional[PlaceType]
    tags: Optional[str]
    coordinates: Optional[List[str]]
    map_name: Optional[str]

    photo: Optional[ModelPhotoDTO]
    photos: Optional[List[ModelPhotoDTO]]
    model_config = ConfigDict(from_attributes=True)


class ValidatedCreatePlaceDTO(BaseModel):
    city: CityCategory
    name: str
    category: PlaceCategory
    type: Optional[PlaceType]
    tags: Optional[str]
    coordinates: Optional[List[float]]
    map_name: Optional[str]

    photo: Optional[ModelPhotoDTO]
    photos: Optional[List[ModelPhotoDTO]]
    model_config = ConfigDict(from_attributes=True)


class RemovePlacePhotoDTO(BaseModel):
    photo_id: int
