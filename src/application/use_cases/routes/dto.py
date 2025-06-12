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
    ):
        return cls(
            name=name,
            author_id=author_id,
            city=city,
            type=type,
        )


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


class RouteFeedFiltersDTO(BaseModel):
    name: Optional[str] = Field(default=None, description="Поиск маршрута по имени (частичное совпадение)")
    city: Optional[CityCategory] = Field(
        default=CityCategory.PERM, description="Фильтрация по городу. По умолчанию — Пермь"
    )
    type: Optional[RouteType] = Field(default=None, description="Тип маршрута")
    places_count: Optional[int] = Field(
        default=None, description="Фильтрация по ТОЧНОМУ количеству мест в маршруте"
    )
    places_gte: Optional[int] = Field(
        default=None, description="Количество мест в маршруте должно быть БОЛЬШЕ ИЛИ РАВНО этому значению"
    )
    places_lte: Optional[int] = Field(
        default=None, description="Количество мест в маршруте должно быть МЕНЬШЕ ИЛИ РАВНО этому значению"
    )
    has_avatar: Optional[bool] = Field(
        default=None, description="Если True — возвращать только маршруты с аватаркой"
    )
    has_photos: Optional[bool] = Field(
        default=None, description="Если True — возвращать только маршруты с фото"
    )
    is_custom: Optional[bool] = Field(
        default=None, description="Фильтрация по пользовательским маршрутам (True/False)"
    )


class PublicRouteCreateDTO(BaseModel):
    name: str
    city: Optional[CityCategory] = None
    type: Optional[RouteType] = None

    model_config = ConfigDict(from_attributes=True)
