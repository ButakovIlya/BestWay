from datetime import datetime


from pydantic import BaseModel, ConfigDict, Field


class UserCreateDTO(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=10, max_length=15)


class UserUpdateDTO(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=255)


class UserDTO(BaseModel):
    id: int | None = None
    name: str
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
