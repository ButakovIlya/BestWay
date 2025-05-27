from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from application.utils import get_settings
from domain.entities.enums import CityCategory, PlaceCategory, PlaceType, RouteType, SurveyStatus
from domain.filters import BaseFilter
from infrastructure.models.alchemy.routes import Place, Route


class CommonPlaceBase(BaseModel):
    name: str
    category: PlaceCategory
    city: Optional[CityCategory] = None
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
    category: PlaceCategory
    city: CityCategory = None
    type: PlaceType = None
    tags: str = None
    coordinates: List[float] = None
    map_name: str = None


class PlacePatch(CommonPlaceBase):
    name: Optional[str] = None
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
            url=f"{get_settings().app.base_url}{url.lstrip('/')}" if url else "",
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
            city=place.city,
            category=place.category,
            type=place.type,
            tags=place.tags,
            coordinates=place.coordinates,
            photo=f"{get_settings().app.base_url}{place.photo.lstrip('/')}" if place.photo else None,
            map_name=place.map_name,
            photos=[PhotoRead.model_validate(photo) for photo in place.photos] if place.photos else None,
        )


class PlaceFilter(BaseFilter):
    name: Optional[str] = Field(None, description="Partial match for name")
    city: Optional[CityCategory] = None
    category: Optional[PlaceCategory] = None
    type: Optional[PlaceType] = None
    tags: Optional[str] = None
    coordinates: Optional[list] = None
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


class CommonRouteBase(BaseModel):
    name: str
    city: Optional[CityCategory] = None
    type: Optional[RouteType] = None


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
    def model_validate(cls, data: Any) -> "RoutePlaceRead":
        return cls(
            order=getattr(data, "order", 0),
            place=PlaceRead.model_validate(data.place),
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

    @classmethod
    def model_validate(cls, user: Any) -> "UserRead":
        return cls(
            id=user.id,
            phone=user.phone,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            registration_date=user.registration_date,
            is_banned=user.is_banned,
            is_admin=user.is_admin,
            photo=f"{get_settings().app.base_url}{user.photo.lstrip('/')}" if user.photo else None,
            description=user.description,
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

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, route: Route) -> "RouteRead":
        return cls(
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
            places=[RoutePlaceRead.model_validate(place) for place in route.places],
        )


class RouteFilter(BaseFilter):
    name: Optional[str] = Field(None, description="Partial match for name")
    city: Optional[CityCategory] = None
    type: Optional[RouteType] = None

    name__list: Optional[List[str]] = None
    city__list: Optional[List[CityCategory]] = None
    type__list: Optional[List[PlaceType]] = None


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
    author_id: int
    route_id: int
    place_id: int
    timestamp: Optional[datetime] = None


class LikeCreate(LikeBase):
    pass


class LikePut(LikeBase):
    author_id: int
    route_id: int
    place_id: int
    timestamp: Optional[datetime] = None


class LikePatch(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    timestamp: Optional[datetime] = None


class LikeRead(LikeBase):
    id: int

    model_config = {"from_attributes": True}


class LikeFilter(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    timestamp: Optional[datetime] = None

    author_id__list: Optional[List[int]] = None
    route_id__list: Optional[List[int]] = None
    place_id__list: Optional[List[int]] = None


class CommentBase(BaseModel):
    author_id: int
    route_id: int
    place_id: int
    timestamp: Optional[datetime] = None
    comment: Optional[str] = None
    photo: Optional[str] = None


class CommentCreate(CommentBase):
    pass


class CommentPut(CommentBase):
    author_id: int
    route_id: int
    place_id: int
    timestamp: Optional[datetime] = None
    comment: Optional[str] = None
    photo: Optional[str] = None


class CommentPatch(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    comment: Optional[str] = None
    photo: Optional[str] = None


class CommentRead(CommentBase):
    id: int

    model_config = {"from_attributes": True}


class CommentFilter(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    timestamp: Optional[datetime] = None
    comment: Optional[str] = None
    photo: Optional[str] = None

    author_id__list: Optional[List[int]] = None
    route_id__list: Optional[List[int]] = None
    place_id__list: Optional[List[int]] = None
