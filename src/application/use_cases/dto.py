from enum import Enum

from domain.validators.dto import ColumnType

from pydantic import BaseModel


class ColumnInfo(BaseModel):
    label: str | Enum
    name: str
    type: ColumnType | None
    regex: str | None
