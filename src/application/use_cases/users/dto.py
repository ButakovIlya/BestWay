from io import BytesIO
from typing import Optional, Annotated

from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict, Field, StringConstraints


class UserCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=15)


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


class UserListFullOutputDTO(UserDTO):
    pass


class PhoneNumberDTO(BaseModel):
    phone: str  = Field(None, min_length=10, max_length=15)


class PhoneCodeDTO(BaseModel):
    code: str  = Field(None, max_length=4, min_length=4)


class UserRetrieveDTO(BaseModel):
    user_id: int



class UserUpdateDTO(BaseModel):
    first_name: Optional[Annotated[str, StringConstraints(max_length=255)]] = None
    email: Optional[EmailStr] = None
    phone: Optional[Annotated[str, StringConstraints(pattern=r'^\d{11}$')]] = None
    photo: Optional[BytesIO] = None
    filename: Optional[str] = None

    model_config = {
        "arbitrary_types_allowed": True
    }