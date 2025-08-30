from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from application.use_cases.common.dto import ModelPhotoDTO


class PostDTO(BaseModel):
    id: int
    title: str
    description: Optional[str]
    route_id: int
    author_id: int
    photo: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CreatePostDTO(BaseModel):
    title: str
    description: Optional[str]
    route_id: int

    photo: Optional[ModelPhotoDTO]

    model_config = ConfigDict(from_attributes=True)


class ValidatedCreatePostDTO(BaseModel):
    title: str
    description: Optional[str]
    route_id: int

    photo: Optional[ModelPhotoDTO]
    photos: Optional[List[ModelPhotoDTO]]

    model_config = ConfigDict(from_attributes=True)


class RemovePostPhotoDTO(BaseModel):
    photo_id: int
