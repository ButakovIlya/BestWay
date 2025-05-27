from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class LikeDTO(BaseModel):
    id: int
    author_id: int
    route_id: Optional[int]
    place_id: Optional[int]
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class CommentDTO(BaseModel):
    id: int
    author_id: int
    route_id: Optional[int]
    place_id: Optional[int]
    timestamp: datetime
    comment: Optional[str]
    photo: Optional[str]

    model_config = ConfigDict(from_attributes=True)
