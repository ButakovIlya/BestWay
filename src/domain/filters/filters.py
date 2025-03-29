from typing import Any

from pydantic import BaseModel, field_validator


class BaseFilter(BaseModel):
    @field_validator("*", mode="before")
    @classmethod
    def normalize_lists(cls, v: Any, info):
        field_name = info.field_name
        if not field_name.endswith("__list"):
            return v
        if v is None:
            return []
        if isinstance(v, str):
            v = [v]
        return v
