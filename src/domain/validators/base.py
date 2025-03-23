import re
from pydantic import BaseModel, Field, field_validator

class PhoneNumberValidator(BaseModel):
    phone: str = Field(..., example="+7(999)123-45-67")

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Приводит телефон к формату 79991234567 и проверяет его корректность."""
        # Удаляем все, кроме цифр
        cleaned_phone = re.sub(r"\D", "", value)

        # Если номер начинается с 8, заменяем его на 7
        if cleaned_phone.startswith("8"):
            cleaned_phone = "7" + cleaned_phone[1:]

        if not re.match(r"^7\d{10}$", cleaned_phone):
            raise ValueError("Некорректный номер телефона. Формат: 79991234567")

        return cleaned_phone
