from datetime import datetime
from typing import Any

from pydantic import BaseModel

from application.utils import get_settings


class UserRead(BaseModel):
    id: int
    phone: str
    first_name: str | None = None
    last_name: str | None = None
    middle_name: str | None = None
    registration_date: datetime | None = None
    is_banned: bool = False
    is_admin: bool = False
    photo: str | None = None
    description: str | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, user: Any) -> "UserRead":
        if not user:
            return None
        return cls(
            id=user.id,
            phone=user.phone,
            first_name=user.first_name,
            last_name=user.last_name,
            middle_name=user.middle_name,
            registration_date=user.registration_date,
            is_banned=user.is_banned,
            is_admin=user.is_admin,
            photo=f"{get_settings().app.base_url}/{user.photo.lstrip('/')}" if user.photo else None,
            description=user.description,
        )
