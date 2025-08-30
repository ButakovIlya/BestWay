from datetime import datetime
from typing import Optional

from domain.entities.entity import Entity


class Post(Entity):
    def __init__(
        self,
        id: Optional[int] = None,
        route_id: Optional[int] = None,
        author_id: Optional[int] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        photo: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        author: Optional[dict] = None,
        route: Optional[dict] = None,
    ) -> None:
        super().__init__(id)

        self.route_id = route_id
        self.author_id = author_id
        self.title = title
        self.description = description
        self.photo = photo
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

        self.author = author
        self.route = route
