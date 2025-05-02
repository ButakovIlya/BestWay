from datetime import datetime
from io import BytesIO
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from common.exceptions import APIException
from domain.entities.enums import CityCategory, RouteType


class RouteCreateDTO(BaseModel):
    name: str
    author_id: int
    city: Optional[CityCategory] = None
    type: Optional[RouteType] = None
    duration: Optional[int] = None
    distance: Optional[int] = None
    json_data: Optional[str] = Field(None, alias="json")
    places: List[int] = []

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def from_form(
        cls,
        name: str,
        author_id: int,
        city: Optional[CityCategory],
        type: Optional[RouteType],
        duration: Optional[str],
        distance: Optional[str],
        json: Optional[str],
        places: Optional[str],
    ):
        try:
            places_list = [int(p.strip()) for p in places.split(",") if p.strip()]
        except ValueError:
            raise APIException(code=400, message="Places must be a list of integers")

        return cls(
            name=name,
            author_id=author_id,
            city=city,
            type=type,
            json=json,
            duration=duration,
            distance=distance,
            places=places_list,
        )


class UserRead(BaseModel):
    id: int
    phone: str
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    registration_date: datetime | None = None
    is_banned: bool = False
    is_admin: bool = False
    photo: str | None = None
    description: str | None = None

    model_config = {"from_attributes": True}


class RouteDTO(BaseModel):
    id: int
    name: str
    author_id: int
    duration: Optional[int] = None
    distance: Optional[int] = None
    photos: List[Optional[BytesIO]] = None
    photo: Optional[BytesIO] = None
    places: List[int] = []

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
