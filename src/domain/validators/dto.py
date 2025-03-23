from enum import Enum
from typing import TypeAlias

from pydantic import BaseModel


class ResourceTechnicalValidationError(BaseModel):
    field: str
    message: str = ""


class ResourceDuplicateValidationError(BaseModel):
    fields: list[str]
    indexes: list[int]


ResourceValidationError: TypeAlias = (
    ResourceTechnicalValidationError | ResourceDuplicateValidationError
)


class ColumnType(str, Enum):
    string = "string"
    number = "number"
    date = "date"
    select = "select"
