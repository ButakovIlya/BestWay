from domain.entities.entity import Entity
from domain.entities.enums import PlaceCategory, PlaceType


class Place(Entity):
    def __init__(
        self,
        id: int | None = None,
        name: str | None = None,
        category: PlaceCategory | None = None,
        type: PlaceType | None = None,
        tags: str | None = None,
        coordinates: str | None = None,
        photo: str | None = None,
        map_name: str | None = None,

    ) -> None:
        super().__init__(id)

        self.name = name
        self.category = category
        self.type = type
        self.tags = tags
        self.coordinates = coordinates
        self.photo = photo
        self.map_name = map_name
