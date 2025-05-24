from datetime import date
from typing import Dict, List, Optional

from pydantic import BaseModel, model_validator

from domain.entities.enums import CityCategory, Gender, PlaceCategory, PlaceType, RouteType


class ChatGPTUserData(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    middle_name: Optional[str]
    description: Optional[str]
    gender: Optional[Gender]
    birth_date: Optional[date]


class ChatGPTPlaceData(BaseModel):
    id: int
    name: str
    category: str
    type: Optional[str] = None
    tags: Optional[str] = None
    coordinates: List[float] | None = None
    map_name: Optional[str] = None


class ChatGPTSurveyData(BaseModel):
    data: Optional[dict] = None
    places: Optional[dict] = None
    city: Optional[CityCategory] = CityCategory.PERM


class ChatGPTContentData(BaseModel):
    user_data: ChatGPTUserData
    survey_data: ChatGPTSurveyData
    places_data: List[ChatGPTPlaceData]


class ChatGPTRouteData(BaseModel):
    name: Optional[str] = "Сгенерированный маршрут"
    type: RouteType
    places: List[int]
    author_id: int


class PlaceInfo(BaseModel):
    place_id: Optional[int] = None
    category: Optional[PlaceCategory] = None
    type: Optional[PlaceType] = None
    description: Optional[str] = None

    @model_validator(mode="after")
    def at_least_one_field_must_be_filled(self):
        if not any(
            [
                self.place_id is not None,
                self.category is not None,
                self.type is not None,
                self.description is not None,
            ]
        ):
            raise ValueError("At least one of place_id, category, type, or description must be provided.")
        return self


class SurveyPlacesInfo(BaseModel):
    places: Dict[int, PlaceInfo]


# data = {
#     1: "Галерея 1",
#     2: "Любой музей",
#     3: "Любой итальянский ресторан",
#     4: "Любое классное место",
# }


data = {
    1: PlaceInfo(place_id=1),
    2: PlaceInfo(category=PlaceCategory.MUSEUM),
    3: PlaceInfo(category=PlaceCategory.RESTAURANT, type=PlaceType.ITALIAN),
    4: PlaceInfo(description="Подбери любое место на свой вкус"),
}
