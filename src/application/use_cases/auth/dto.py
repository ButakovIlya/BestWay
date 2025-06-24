from typing import Optional

from pydantic import BaseModel, Field, field_validator

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


class ChangePhoneSmsPayloadDTO(BaseModel):
    """DTO для передачи данных SMS для смены телефона."""

    phone: Optional[str] = Field(example="79991234567", default=None)
    new_phone: str = Field(..., example="79991234567")
    code: str = Field(..., example="1234", min_length=4, max_length=4, pattern=r"^\d{4}$")

    @field_validator("phone", "new_phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Использует валидатор `PhoneNumberValidator` для нормализации телефона."""
        return PhoneNumberValidator(phone=value).phone


class TokenDTO(BaseModel):
    """DTO для ответа при успешной верификации кода."""

    status: str = Field("ok", example="ok")
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1N...")
    refresh_token: str = Field(..., example="dGhpcyBpcyBhIHJlZnJlc2g...")

    is_new_user: bool = Field(False, example=False)
    user_id: int = Field(..., example=1)
