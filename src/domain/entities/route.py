from datetime import datetime
from typing import List, Optional

from domain.entities.entity import Entity
from domain.entities.enums import CityCategory, RouteType


class Route(Entity):
    def __init__(
        self,
        id: Optional[int] = None,
        name: Optional[str] = None,
        city: CityCategory = CityCategory.PERM,
        type: RouteType = RouteType.MIXED,
        is_publicated: bool = False,
        photo: str | None = None,
        photos: List[str] | None = None,
        author_id: Optional[int] = None,
        author: Optional[dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        duration: Optional[int] = None,
        distance: Optional[int] = None,
        is_custom: Optional[bool] = False,
        json_data: Optional[dict] = None,
        places: Optional[List[int]] = None,
        photo_ids: Optional[List[int]] = None,
        like_ids: Optional[List[int]] = None,
        comment_ids: Optional[List[int]] = None,
    ) -> None:
        super().__init__(id)

        self.name = name
        self.city = city
        self.author_id = author_id
        self.author = author
        self.photo = photo
        self.photos = photos
        self.type = type
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.duration = duration
        self.distance = distance
        self.is_custom = is_custom
        self.is_publicated = is_publicated
        self.json_data = json_data

        self.places = places or []
        self.photo_ids = photo_ids or []
        self.like_ids = like_ids or []
        self.comment_ids = comment_ids or []
