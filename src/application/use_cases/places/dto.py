from typing import Optional

from pydantic import BaseModel, ConfigDict

from domain.entities.enums import PlaceCategory, PlaceType


class PlaceDTO(BaseModel):
    id: Optional[int]
    name: Optional[str]
    category: Optional[PlaceCategory]
    type: Optional[PlaceType]
    tags: Optional[str]
    coordinates: Optional[str]
    photo: Optional[str]
    map_name: Optional[str]

    model_config = ConfigDict(from_attributes=True)
