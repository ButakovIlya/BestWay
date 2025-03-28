from io import BytesIO
from typing import Optional

from pydantic import BaseModel

from infrastructure.managers.enum import ModelType


class ObjectPhotoDTO(BaseModel):
    photo: Optional[BytesIO] = None
    filename: Optional[str] = None
    filepath: Optional[str] = None
    model_name: ModelType

    photo_field: Optional[str] = "photo"

    class Config:
        arbitrary_types_allowed = True
