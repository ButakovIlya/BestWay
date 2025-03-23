from domain.entities.entity import Entity


class Resource(Entity):
    def __init__(
        self,
        id: int | None,
    ) -> None:
        super().__init__(id)
