from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from application.constants import MIN_PLACES_COUNT
from domain.entities.enums import RouteType, SurveyStatus


class CommonSurveyDTO(BaseModel):
    name: Optional[str]
    data: Optional[Dict]
    status: Optional[SurveyStatus]

    model_config = ConfigDict(from_attributes=True)


class SurveyCreateDTO(CommonSurveyDTO):
    name: str = Field(..., example="Опрос по благоустройству")
    status: Optional[SurveyStatus] = Field(default=SurveyStatus.DRAFT)


class SurveyPutDTO(CommonSurveyDTO):
    author_id: int
    status: SurveyStatus


class SurveyPatchDTO(CommonSurveyDTO):
    author_id: Optional[int]


class SurveyDTO(CommonSurveyDTO):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime


class SurveyDataUpdateDTO(BaseModel):
    experience: Optional[str]
    answers: Optional[Dict[str, str]]  # произвольные пары "вопрос: ответ"
    # locations: Optional[List[int]]
    order_matters: Optional[bool] = False  # "важен ли порядок"
    preferred_transport: Optional[RouteType]
    route_preferences: Optional[str]

    places_count: Optional[int] = MIN_PLACES_COUNT

    @field_validator("experience", "route_preferences")
    def validate_length(cls, v, field):
        if v is not None and len(v) > 250:
            raise ValueError(f"{field.name} не может содержать больше 250 символов")
        return v

    @field_validator("places_count")
    def validate_length(cls, v, field):
        if v is not None and v < MIN_PLACES_COUNT:
            raise ValueError(f"{field.name} не может быть меньше {MIN_PLACES_COUNT}")
        return v

    # @field_validator("locations", each_item=True)
    # def validate_location_item(cls, loc_dict):
    #     if not isinstance(loc_dict, dict):
    #         raise ValueError("Каждая локация должна быть словарём")
    #     for name, coords in loc_dict.items():
    #         if not isinstance(name, str) or not isinstance(coords, str):
    #             raise ValueError("Ключ и значение должны быть строками")
    #         parts = coords.split(",")
    #         if len(parts) != 2:
    #             raise ValueError(f"Координаты должны быть в формате 'широта,долгота', а не '{coords}'")
    #         try:
    #             float(parts[0].strip())
    #             float(parts[1].strip())
    #         except ValueError:
    #             raise ValueError(f"Координаты '{coords}' содержат нечисловые значения")
    #     return loc_dict
