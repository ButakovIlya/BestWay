from enum import Enum
from typing import TypeAlias

from pydantic import BaseModel


class ResourceTechnicalValidationError(BaseModel):
    field: str
    message: str = ""


class ResourceDuplicateValidationError(BaseModel):
    fields: list[str]
    indexes: list[int]


