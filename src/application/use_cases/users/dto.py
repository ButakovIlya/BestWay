from datetime import date, datetime
from io import BytesIO
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from domain.entities.enums import Gender


class CommonUserDTO(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, min_length=1, max_length=255)
    middle_name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    gender: Optional[Gender] = None
    birth_date: Optional[date] = None  # формат "YYYY-MM-DD"

    @field_validator("birth_date", mode="before")
    @classmethod
    def parse_birth_date(cls, value):
        if isinstance(value, str):
            try:
                return date.fromisoformat(value)
            except ValueError:
                raise ValueError("birth_date должен быть в формате 'YYYY-MM-DD'")
        return value

    @field_validator("birth_date")
    @classmethod
    def check_minimum_age(cls, value: Optional[date]) -> Optional[date]:
        if value is not None:
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 14:
                raise ValueError("Пользователь должен быть старше 14 лет")
        return value

    model_config = ConfigDict(from_attributes=True)


class UserDTO(CommonUserDTO):
    id: Optional[int] = None
    phone: str
    registration_date: Optional[datetime] = None
    is_banned: bool = False
    is_admin: bool = False
    photo: Optional[str] = None
    gender: Optional[str]
    model_config = dict(from_attributes=True)


class UserCreateDTO(CommonUserDTO):
    phone: str = Field(..., min_length=10, max_length=15)
    is_admin: Optional[bool] = Field(default=False)


class UserUpdateDTO(CommonUserDTO):
    email: Optional[str] = None


class FullUserUpdateDTO(CommonUserDTO):
    email: Optional[EmailStr] = None
    is_banned: Optional[bool] = None
    is_admin: Optional[bool] = None

    class Config:
        from_attributes = True


class UserDeleteDTO(BaseModel):
    phone: str = Field(..., min_length=10, max_length=15)


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
