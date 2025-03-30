from typing import Any, List, Optional

from pydantic import BaseModel

from domain.entities.enums import ModelType


class ModelFieldValuesData(BaseModel):
    results: List[Optional[Any]]
    count: int
    next: int | None = None
    previous: int | None = None


class ModelFieldValuesInputDTO(BaseModel):
    per_page: int | None = None
    page: int | None = None
    model_name: ModelType
    name: str
