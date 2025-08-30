import json
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from application.constants import MAX_FIELD_SIZE, MAX_PLACES_COUNT, MAX_PROMPT_LENGHT, MIN_PLACES_COUNT
from domain.entities.enums import CityCategory, PlaceCategory, PlaceType, RouteType, SurveyStatus


class CommonSurveyDTO(BaseModel):
    name: Optional[str]
    city: Optional[CityCategory]
    data: Optional[Dict]
    prompt: Optional[str]
    places: Optional[Dict]
    status: Optional[SurveyStatus]

    model_config = ConfigDict(from_attributes=True)


class SurveyCreateDTO(BaseModel):
    name: str = Field(..., example="Опрос по предпочтениям")
    city: Optional[CityCategory] = CityCategory.PERM

    model_config = ConfigDict(from_attributes=True)


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


class PlaceInfo(BaseModel):
    place_id: Optional[int] = Field(default=None, description="ID места из БД")
    category: Optional[PlaceCategory] = Field(default=None, description="Категория места")
    type: Optional[PlaceType] = Field(default=None, description="Тип места")
    description: Optional[str] = Field(max_length=50, default=None, description="Краткое описание")

    @model_validator(mode="after")
    def at_least_one_field_must_be_filled(self):
        if not any([self.place_id, self.category, self.type, self.description]):
            raise ValueError("At least one of place_id, category, type, or description must be provided.")
        return self

    model_config = {"from_attributes": True, "use_enum_values": True}


class SurveyDataUpdateDTO(BaseModel):
    experience: Optional[str] = Field(default=None, description="Опыт пользователя")
    questions: Optional[Dict[str, str]] = Field(default=None, description="Ответы на вопросы, до 2048 байт")
    preferences: Optional[str] = Field(default=None, description="Предпочтения пользователя")
    preferred_transport: Optional[RouteType] = Field(
        default=RouteType.MIXED.value, description="Предпочтительный транспорт"
    )
    places_count: Optional[int] = Field(default=MIN_PLACES_COUNT, description="Количество мест")
    order_matters: Optional[bool] = Field(
        default=False, description="Учитывается ли порядок посещения мест"
    )

    @field_validator("questions")
    def validate_questions_size(cls, v):
        if v is not None:
            byte_size = len(json.dumps(v, ensure_ascii=False).encode("utf-8"))
            if byte_size > MAX_FIELD_SIZE:
                raise ValueError(f"Поле 'questions' не может превышать {MAX_FIELD_SIZE} байт")
        return v

    @field_validator("experience", "preferences")
    def validate_length(cls, v, field):
        if v is not None and len(v) > 250:
            raise ValueError(f"experience и preferences не может содержать больше 250 символов")
        return v

    @field_validator("places_count")
    def validate_length_places_count(cls, v, field):
        if v is not None and v < MIN_PLACES_COUNT:
            raise ValueError(f"places_count не может быть меньше {MIN_PLACES_COUNT}")
        return v

    model_config = {"from_attributes": True, "use_enum_values": True}


class SurveyUpdateDTO(BaseModel):
    name: Optional[str] = "Анкета маршрута"
    city: Optional[CityCategory] = CityCategory.PERM.value
    data: Optional[SurveyDataUpdateDTO] = None
    prompt: Optional[str] = None
    places: Optional[Dict[int, PlaceInfo]] = None

    @field_validator("prompt")
    def validate_prompt_length(cls, v, _):
        if v is not None and len(v) > MAX_PROMPT_LENGHT:
            raise ValueError(f"Промпт не может быть длинее {MAX_PROMPT_LENGHT}")
        return v

    @model_validator(mode="after")
    def validate_places_keys(self):
        if self.places:
            keys = sorted(self.places.keys())
            if keys[0] != 1:
                raise ValueError("Нумерация мест должна начинаться с 1.")
            if keys != list(range(1, len(keys) + 1)):
                raise ValueError("Номера мест должны быть последовательными: 1, 2, 3, ...")
            if len(keys) > MAX_PLACES_COUNT:
                raise ValueError(f"Нельзя выбрать больше {MAX_PLACES_COUNT} мест.")
        return self

    model_config = ConfigDict(from_attributes=True)
