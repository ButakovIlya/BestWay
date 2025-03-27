from datetime import datetime
from domain.entities.entity import Entity
from infrastructure.permissions.enums import RoleEnum


class User(Entity):
    def __init__(
        self,
        phone: str,
        id_admin: bool = False,
        role: RoleEnum = RoleEnum.USER,
        id: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        middle_name: str | None = None,
        is_banned: bool | None = None,
        is_admin: bool | None = None,
        photo: str | None = None,
        description: str | None = None,
        registration_date: datetime | None = None,
    ) -> None:
        super().__init__(id)
        self.phone = phone
        self.id_admin = id_admin
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.is_banned = is_banned
        self.is_admin = is_admin
        self.photo = photo
        self.description = description

        self.registration_date = registration_date
