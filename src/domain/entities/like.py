from datetime import datetime
from typing import Optional

from domain.entities.entity import Entity


class Like(Entity):
    def __init__(
        self,
        id: Optional[int] = None,
        author_id: Optional[int] = None,
        route_id: Optional[int] = None,
        place_id: Optional[int] = None,
        post_id: Optional[int] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        super().__init__(id)
        self.author_id = author_id
        self.route_id = route_id
        self.place_id = place_id
        self.post_id = post_id
        self.timestamp = timestamp or datetime.now()
