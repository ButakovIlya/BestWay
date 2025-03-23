from abc import abstractmethod
from typing import TypeVar

from domain.entities.resource import Resource
from infrastructure.repositories.interfaces.base import ResourceRepository

TResource = TypeVar("TResource", bound=Resource)

class UserRepository(ResourceRepository):
    @abstractmethod
    async def get_by_phone(self, phone: str) -> TResource:
        """Получить пользователя по телефону"""
        pass
