from typing import Optional

from pydantic import BaseModel, Field, field_validator
from application.use_cases.users.dto import UserUpdateDTO
from domain.validators import PhoneNumberValidator


class PhoneDTO(BaseModel):
    """DTO для передачи номера телефона."""
    phone: str = Field(..., example="79991234567")


class SmsResponseDTO(BaseModel):
    """DTO для ответа после отправки SMS."""
    message: str = Field(..., example="Код отправлен")


class SmsPayloadDTO(BaseModel):
    """DTO для передачи данных SMS."""
    phone: str = Field(..., example="79991234567")
    code: str = Field(..., example="1234", min_length=4, max_length=4, pattern=r"^\d{4}$")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Использует валидатор `PhoneNumberValidator` для нормализации телефона."""
        return PhoneNumberValidator(phone=value).phone


class TokenDTO(BaseModel):
    """DTO для ответа при успешной верификации кода."""
    status: str = Field("ok", example="ok")
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1N...")
    refresh_token: str = Field(..., example="dGhpcyBpcyBhIHJlZnJlc2g...")


from fastapi import Form, File, UploadFile
from typing import Annotated
from io import BytesIO

async def get_user_update_dto(
    first_name: Annotated[Optional[str], Form()] = None,
    last_name: Annotated[Optional[str], Form()] = None,
    middle_name: Annotated[Optional[str], Form()] = None,
    email: Annotated[Optional[str], Form()] = None,
    phone: Annotated[Optional[str], Form()] = None,
    description: Annotated[Optional[str], Form()] = None,
    photo: Annotated[Optional[UploadFile], File()] = None,
) -> UserUpdateDTO:
    dto = UserUpdateDTO(
        first_name=first_name,
        last_name=last_name,
        middle_name=middle_name,
        email=email,
        phone=phone,
        description=description,
    )

    if photo:
        dto._filename = photo.filename
        dto._photo = BytesIO(await photo.read())

    return dto
