from io import BytesIO
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from api.admin.schemas import PlaceSchema


class RouteCreateDTO(BaseModel):
    name: str
    author: int
    duration: Optional[int] = None
    distance: Optional[int] = None
    photos: List[Optional[BytesIO]] = None
    places: List[PlaceSchema] = []

    model_config = ConfigDict(from_attributes=True)
