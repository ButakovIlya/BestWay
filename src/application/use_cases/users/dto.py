from datetime import datetime
from io import BytesIO
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserDTO(BaseModel):
    id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    phone: str
    registration_date: datetime | None = None
    is_banned: bool = False
    is_admin: bool = False
    photo: str | None = None
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)


class UserCreateDTO(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)
    first_name: str | None = Field(None, min_length=1, max_length=255)
    last_name: str | None = Field(None, min_length=1, max_length=255)
    middle_name: str | None = Field(None, min_length=1, max_length=255)
    is_admin: bool | None = Field(default=False)


class UserDeleteDTO(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)


class UserUpdateDTO(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[str] = None
    description: Optional[str] = None


class FullUserUpdateDTO(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[EmailStr] = None
    description: Optional[str] = None
    is_banned: Optional[bool] = None
    is_admin: Optional[bool] = None

    class Config:
        from_attributes = True


class UserListFullOutputDTO(UserDTO):
    pass


class PhoneNumberDTO(BaseModel):
    phone: str = Field(None, min_length=10, max_length=15)


class PhoneCodeDTO(BaseModel):
    code: str = Field(None, max_length=4, min_length=4)


class UserRetrieveDTO(BaseModel):
    user_id: int


class UserPhotoDTO(BaseModel):
    photo: Optional[BytesIO] = None
    filename: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
