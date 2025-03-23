class Entity:
    def __init__(self, id: int | None) -> None:
        self.id = id

    def __repr__(self) -> str:
        attributes = {
            attribute.strip("_") if attribute.startswith("_") else attribute: value
            for attribute, value in vars(self).items()
        }
        attributes_repr = ", ".join(
            f"{key}={value}" for key, value in attributes.items()
        )
        return f"{self.__class__.__name__}({attributes_repr})"
