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


class LikeCreate(BaseModel):
    route_id: Optional[int] = None
    place_id: Optional[int] = None


class LikeCreateDTO(BaseModel):
    author_id: int
    route_id: Optional[int] = None
    place_id: Optional[int] = None


class LikeRemoveDTO(BaseModel):
    author_id: int
    route_id: Optional[int] = None
    place_id: Optional[int] = None


class LikeBase(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None


class LikeRead(LikeBase):
    id: int
    timestamp: Optional[datetime] = None

    model_config = {"from_attributes": True}
