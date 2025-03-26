from abc import abstractmethod
from typing import TypeVar

from domain.entities.model import Model
from infrastructure.repositories.interfaces.base import ModelRepository

TModel = TypeVar("TModel", bound=Model)

class UserRepository(ModelRepository):
    @abstractmethod
    async def get_by_phone(self, phone: str) -> TModel:
        """Получить пользователя по телефону"""
        pass

    @abstractmethod
    async def exists_by_phone(self, phone: str) -> bool:
        """Получить пользователя по телефону"""
        pass

    @abstractmethod
    async def delete_by_phone(self, phone: str) -> bool:
        """Удалить пользователя по телефону"""
        pass
