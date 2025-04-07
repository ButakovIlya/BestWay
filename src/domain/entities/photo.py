from datetime import datetime
from typing import Optional

from domain.entities.entity import Entity


class Photo(Entity):
    def __init__(
        self,
        id: Optional[int] = None,
        url: Optional[str] = None,
        uploaded_at: Optional[datetime] = None,
        uploaded_by: Optional[int] = None,
        place_id: Optional[int] = None,
        route_id: Optional[int] = None,
    ) -> None:
        super().__init__(id)

        self.url = url
        self.uploaded_at = uploaded_at
        self.uploaded_by = uploaded_by
        self.place_id = place_id
        self.route_id = route_id
