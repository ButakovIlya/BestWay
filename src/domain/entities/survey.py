from datetime import datetime
from typing import Optional

from domain.entities.entity import Entity
from domain.entities.enums import CityCategory, SurveyStatus


class Survey(Entity):
    def __init__(
        self,
        name: str,
        city: CityCategory,
        author_id: int,
        status: SurveyStatus = SurveyStatus.DRAFT,
        data: Optional[dict] = None,
        prompt: Optional[str] = None,
        places: Optional[dict] = None,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ) -> None:
        super().__init__(id)
        self.name = name
        self.city = city
        self.author_id = author_id
        self.status = status
        self.data = data or {}
        self.prompt = prompt
        self.places = places or {}
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
