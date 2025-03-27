from enum import Enum

from pydantic import BaseModel

from domain.validators.dto import ColumnType


class ColumnInfo(BaseModel):
    label: str | Enum
    name: str
    type: ColumnType | None
    regex: str | None
