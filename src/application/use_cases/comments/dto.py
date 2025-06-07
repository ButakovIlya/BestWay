from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field

from application.utils import get_settings
from domain.entities.comment import Comment



class UserRead(BaseModel):
    id: int
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    photo: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, user: Any) -> "UserRead":
        if not user:
            return None
        return cls(
            id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            photo=f"{get_settings().app.base_url}/{user.photo.lstrip('/')}" if user.photo else None,
            description=user.description,
        )


class CommentDTO(BaseModel):
    id: int
    author_id: int
    route_id: Optional[int]
    place_id: Optional[int]
    timestamp: datetime
    comment: Optional[str]
    photo: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    comment: str = Field(max_length=250, min_length=1)


class CommentCreateDTO(BaseModel):
    author_id: int
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    comment: str = Field(max_length=250, min_length=1)


class CommentRemoveDTO(BaseModel):
    author_id: int
    route_id: Optional[int] = None
    place_id: Optional[int] = None


class CommentBase(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    comment: str = Field(max_length=250, min_length=1)


class CommentRead(CommentBase):
    id: int
    author_id: int
    timestamp: Optional[datetime] = None
    author: Optional[UserRead] = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, comment: Comment) -> "CommentRead":
        return cls(
            id=comment.id,
            author_id=comment.author_id,
            route_id=comment.route_id,
            place_id=comment.place_id,
            comment=comment.comment,
            timestamp=comment.timestamp,
            author=UserRead.model_validate(comment.author) if comment.author else None,
        )


class CommentBaseDTO(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None


class CommentTextDTO(BaseModel):
    comment: str = Field(max_length=250, min_length=1)
