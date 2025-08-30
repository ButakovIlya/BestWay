from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from common.dto import UserRead
from domain.entities.comment import Comment


class CommentDTO(BaseModel):
    id: int
    author_id: int
    route_id: Optional[int]
    place_id: Optional[int]
    post_id: Optional[int]
    timestamp: datetime
    comment: Optional[str]
    photo: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None
    comment: str = Field(max_length=250, min_length=1)


class CommentCreateDTO(BaseModel):
    author_id: int
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None
    comment: str = Field(max_length=250, min_length=1)


class CommentRemoveDTO(BaseModel):
    author_id: int
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None


class CommentBase(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None
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
            post_id=comment.post_id,
            comment=comment.comment,
            timestamp=comment.timestamp,
            author=UserRead.model_validate(comment.author) if comment.author else None,
        )


class CommentBaseDTO(BaseModel):
    author_id: Optional[int] = None
    route_id: Optional[int] = None
    place_id: Optional[int] = None
    post_id: Optional[int] = None


class CommentTextDTO(BaseModel):
    comment: str = Field(max_length=250, min_length=1)
