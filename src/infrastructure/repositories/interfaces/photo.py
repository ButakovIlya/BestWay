from abc import abstractmethod
from typing import TypeVar

from domain.entities.model import Model
from infrastructure.repositories.interfaces.base import ModelRepository

TModel = TypeVar("TModel", bound=Model)


class PhotoRepository(ModelRepository):
    @abstractmethod
    async def update_photo(self, phone: str) -> TModel:
        """Сменить фото"""
        pass
