from typing import Optional

from domain.entities.entity import Entity


class RoutePlaces(Entity):
    def __init__(
        self,
        id: Optional[int] = None,
        route_id: Optional[int] = None,
        place_id: Optional[int] = None,
        order: Optional[int] = None,
    ) -> None:
        super().__init__(id)

        self.route_id = route_id
        self.place_id = place_id
        self.order = order
