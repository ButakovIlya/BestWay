from datetime import date, datetime
from typing import List, Optional

from domain.entities.entity import Entity
from domain.entities.enums import Gender
from domain.entities.survey import Survey
from infrastructure.permissions.enums import RoleEnum


class User(Entity):
    def __init__(
        self,
        phone: str,
        is_admin: bool = False,
        role: RoleEnum = RoleEnum.USER,
        gender: Optional[Gender] = None,
        birth_date: Optional[date] = None,
        id: Optional[int] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        middle_name: Optional[str] = None,
        is_banned: Optional[bool] = None,
        photo: Optional[str] = None,
        description: Optional[str] = None,
        registration_date: Optional[datetime] = None,
        surveys: Optional[List[Survey]] = None,
    ) -> None:
        super().__init__(id)
        self.phone = phone
        self.is_admin = is_admin
        self.role = role
        self.gender = gender
        self.birth_date = birth_date
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name
        self.is_banned = is_banned
        self.photo = photo
        self.description = description
        self.registration_date = registration_date
        self.surveys = surveys or []
