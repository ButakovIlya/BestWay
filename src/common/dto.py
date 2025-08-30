from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator, validator

from application.utils import get_settings
from domain.entities.enums import CityCategory, PlaceCategory, PlaceType, RouteType
from domain.entities.place import Place
from domain.entities.route import Route


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

    @classmethod
    def model_validate(cls, user: Any) -> "UserRead":
        if not user:
            return None
        return cls(
            id=user.id,
            phone=user.phone,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            registration_date=user.registration_date,
            is_banned=user.is_banned,
            is_admin=user.is_admin,
            photo=f"{get_settings().app.base_url}/{user.photo.lstrip('/')}" if user.photo else None,
            description=user.description,
        )


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
            url=f"{get_settings().app.base_url}/{url.lstrip('/')}" if url else "",
        )


class CommonRouteBase(BaseModel):
    name: str
    city: Optional[CityCategory] = None
    type: Optional[RouteType] = None


class CommonPlaceBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: PlaceCategory
    city: Optional[CityCategory] = None
    object_id: Optional[int] = None
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
            description=place.description,
            city=place.city,
            category=place.category,
            type=place.type,
            tags=place.tags,
            coordinates=place.coordinates,
            object_id=place.object_id,
            photo=f"{get_settings().app.base_url}/{place.photo.lstrip('/')}" if place.photo else None,
            map_name=place.map_name,
            photos=[PhotoRead.model_validate(photo) for photo in place.photos] if place.photos else None,
        )


class RoutePlaceRead(BaseModel):
    order: int
    place: PlaceRead

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, data: Any) -> "RoutePlaceRead":
        return cls(
            order=getattr(data, "order", 0),
            place=PlaceRead.model_validate(data.place),
        )


class RouteRead(CommonRouteBase):
    id: int
    author_id: int
    photo: Optional[str]
    duration: Optional[int]
    distance: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    author: Optional[UserRead] = None
    photos: Optional[List[PhotoRead]]
    places: list[RoutePlaceRead]

    yandex_maps_url: Optional[str] = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, route: Route) -> "RouteRead":
        sorted_places = sorted(route.places, key=lambda p: p.order)

        obj = cls(
            id=route.id,
            name=route.name,
            city=route.city,
            type=route.type,
            photo=route.photo,
            author_id=route.author_id,
            duration=route.duration,
            distance=route.distance,
            created_at=route.created_at,
            updated_at=route.updated_at,
            author=UserRead.model_validate(route.author),
            photos=[PhotoRead.model_validate(p) for p in route.photos],
            places=([RoutePlaceRead.model_validate(place) for place in sorted_places]),
        )
        obj.yandex_maps_url = obj._compute_yandex_maps_url()
        return obj

    def _compute_yandex_maps_url(self) -> Optional[str]:
        if not self.places:
            return None

        # Сортировка по порядку
        sorted_places = sorted(self.places, key=lambda x: x.order)

        # Сбор координат в формате широта,долгота
        coords = "~".join(
            f"{p.place.coordinates[0]},{p.place.coordinates[1]}"
            for p in sorted_places
            if p.place and p.place.coordinates
        )

        # Сбор ruri (если есть object_id / oid)
        ruris = "~".join(
            f"ymapsbm1:/org?oid={p.place.object_id}"
            for p in sorted_places
            if p.place and getattr(p.place, "object_id", None) not in (None, "", 0)
        )
        # Расчёт центра карты (по первой точке)
        first = sorted_places[0].place.coordinates if sorted_places else [0, 0]
        ll = f"{first[1]},{first[0]}"  # долгота,широта

        # Выбор типа маршрута
        rtt_map = {
            RouteType.WALKING: "pd",  # Пешком
            RouteType.CAR: "auto",  # Машина
            RouteType.VEHICLE: "auto",
            RouteType.BUS: "mt",  # Общественный транспорт
            RouteType.SCOOTER_BIKE: "bc",
            RouteType.MIXED: "comparison",  # Смешанный
        }
        rtt_value = rtt_map.get(self.type, "mt")

        # Финальная ссылка
        base = f"https://yandex.ru/maps/?mode=routes&rtext={coords}&rtt={rtt_value}&z=14&ll={ll}"
        if ruris:
            base += f"&ruri={ruris}"
        else:
            base += "&ruri=~~"
        return base


class PlacesFiltersDTO(BaseModel):
    name: Optional[str] = Field(default=None, description="Поиск мест по имени")
    city: Optional[CityCategory] = Field(default="Пермь", description="Фильтрация по городу")
    categories: Optional[str] = Field(default=None, description="Категории через запятую")
    types: Optional[str] = Field(default=None, description="Типы через запятую")
    has_avatar: Optional[bool] = None
    has_photos: Optional[bool] = None

    @field_validator("categories")
    def split_categories(cls, value):
        if isinstance(value, str):
            return [PlaceCategory(item.strip()) for item in value.split(",") if item.strip()]
        return value

    @field_validator("types")
    def split_types(cls, value):
        if isinstance(value, str):
            return [PlaceType(item.strip()) for item in value.split(",") if item.strip()]
        return value


class PostsFiltersDTO(BaseModel):
    title: Optional[str] = Field(default=None, description="Поиск поста по имени (частичное совпадение)")
    description: Optional[str] = Field(
        default=None, description="Поиск поста по описанию (частичное совпадение)"
    )
    route_name: Optional[str] = Field(
        default=None, description="Поиск маршрута по имени (частичное совпадение)"
    )
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
