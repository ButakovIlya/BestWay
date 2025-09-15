from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from application.utils import get_settings
from common.dto import UserRead
from domain.entities.enums import CityCategory, PlaceCategory, PlaceType, RouteType, SurveyStatus
from domain.entities.place import Place
from domain.entities.post import Post
from domain.entities.route import Route
from domain.entities.route_places import RoutePlaces


class CommonPlaceBase(BaseModel):
    name: str
    website_url: Optional[str] = None
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


class PlaceCreate(CommonPlaceBase):
    pass


class PlacePut(CommonPlaceBase):
    name: str
    description: Optional[str] = None
    category: PlaceCategory
    city: CityCategory = None
    type: PlaceType = None
    tags: Optional[str] = None
    coordinates: List[float] = None
    object_id: int | None = None
    map_name: str = None


class PlacePatch(CommonPlaceBase):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[PlaceCategory] = None


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
            website_url=place.website_url,
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


class PhotoSchema(BaseModel):
    url: str


class AuthorSchema(BaseModel):
    id: int
    first_name: str
    last_name: str


class CommonRouteBase(BaseModel):
    name: str
    city: Optional[CityCategory] = None
    type: Optional[RouteType] = None
    is_publicated: bool = False
    description: Optional[str] = None


class MiniRouteSchema(CommonRouteBase):
    id: int
    author_id: int
    duration: Optional[int]
    distance: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class RouteSchema(CommonRouteBase):
    id: int
    author_id: int
    duration: Optional[int]
    distance: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    photos: List[PhotoSchema] = []
    places: List[PlaceRead] = []


class RoutePutSchema(CommonRouteBase):
    name: str
    city: Optional[CityCategory]
    type: Optional[RouteType]
    author: int
    duration: int
    distance: int


class RoutePatchSchema(BaseModel):
    name: Optional[str] = None
    city: Optional[CityCategory] = None
    type: Optional[RouteType] = None
    author: Optional[int] = None
    duration: Optional[int] = None
    distance: Optional[int] = None
    is_publicated: Optional[bool] = False
    description: Optional[str] = None


class RouteCreateSchema(CommonRouteBase):
    id: int
    author: Optional[int] = None
    duration: Optional[int]
    distance: Optional[int]
    places: Optional[List[int]]


class RouteReadSchema(CommonRouteBase):
    id: int
    author_id: int
    duration: Optional[int]
    distance: Optional[int]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    places: List[PlaceRead] = []


class RoutePlaceRead(BaseModel):
    order: int
    place: PlaceRead

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, route_place: RoutePlaces) -> "RoutePlaceRead":
        return cls(
            order=getattr(route_place, "order", 0),
            place=PlaceRead.model_validate(route_place.place),
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
        sorted_places: List[RoutePlaces] = sorted(route.places, key=lambda p: p.order)

        obj = cls(
            id=route.id,
            name=route.name,
            description=route.description,
            city=route.city,
            type=route.type,
            photo=route.photo,
            author_id=route.author_id,
            duration=route.duration,
            distance=route.distance,
            is_publicated=route.is_publicated,
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


class CommonSurveyBase(BaseModel):
    name: str
    city: Optional[CityCategory] = CityCategory.PERM
    status: Optional[SurveyStatus] = SurveyStatus.DRAFT
    data: Optional[dict] = None
    places: Optional[dict] = None


class SurveyCreate(CommonSurveyBase):
    author_id: int


class SurveyPut(CommonSurveyBase):
    name: str
    status: SurveyStatus
    data: dict
    places: dict


class SurveyPatch(CommonSurveyBase):
    name: Optional[str] = None
    status: Optional[SurveyStatus] = None
    data: Optional[dict] = None
    places: Optional[dict] = None


class SurveyRead(CommonSurveyBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, survey: Any) -> "SurveyRead":
        return cls(
            id=survey.id,
            name=survey.name,
            city=survey.city,
            status=survey.status,
            data=survey.data,
            places=survey.places,
            author_id=survey.author_id,
            created_at=survey.created_at,
            updated_at=survey.updated_at,
        )


class SurveyFilter(BaseModel):
    name: Optional[str] = Field(None, description="Partial match for survey name")
    status: Optional[SurveyStatus] = None
    created_at_from: Optional[datetime] = None
    created_at_to: Optional[datetime] = None
    updated_at_from: Optional[datetime] = None
    updated_at_to: Optional[datetime] = None


class LikeBase(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None


class LikeCreate(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None


class LikeRead(LikeBase):
    id: int
    timestamp: Optional[datetime] = None

    model_config = {"from_attributes": True}


class LikeFilter(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None
    timestamp: Optional[datetime] = None

    author_id__list: Optional[List[int]] = None
    route_id__list: Optional[List[int]] = None
    place_id__list: Optional[List[int]] = None
    post_id__list: Optional[List[int]] = None


class CommentBase(BaseModel):
    author_id: int
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    comment: Optional[str] = None
    photo: Optional[str] = None


class CommentPutDTO(CommentBase):
    author_id: int
    route_id: int
    place_id: int
    post_id: int
    comment: Optional[str]


class CommentUpdateDTO(BaseModel):
    comment: str = Field(max_length=250, min_length=1)


class CommentRead(CommentBase):
    id: int

    model_config = {"from_attributes": True}


class CommentFilter(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    comment: Optional[str] = None
    photo: Optional[str] = None

    author_id__list: Optional[List[int]] = None
    route_id__list: Optional[List[int]] = None
    place_id__list: Optional[List[int]] = None
    post_id__list: Optional[List[int]] = None


class CommonPostBase(BaseModel):
    title: str
    description: Optional[str] = None


class PostPut(CommonPostBase):
    title: str
    description: str
    route_id: int


class PostPatch(CommonPostBase):
    title: Optional[str] = None
    description: Optional[str] = None
    route_id: Optional[int] = None


class PostRead(CommonPostBase):
    id: int
    route_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    photo: Optional[str] = None

    author: Optional[UserRead] = None
    route: Optional[RouteRead] = None
    model_config = {"from_attributes": True, "use_enum_values": False}

    @classmethod
    def model_validate(cls, post: Post) -> "PostRead":
        return cls(
            id=post.id,
            title=post.title,
            description=post.description,
            photo=f"{get_settings().app.base_url}/{post.photo.lstrip('/')}" if post.photo else None,
            route_id=post.route_id,
            author_id=post.author_id,
            created_at=post.created_at,
            updated_at=post.updated_at,
            author=UserRead.model_validate(post.author) if post.author else None,
            route=RouteRead.model_validate(post.route) if post.route else None,
        )
