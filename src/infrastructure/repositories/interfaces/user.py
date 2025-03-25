from abc import abstractmethod
from typing import TypeVar

from domain.entities.model import Model
from domain.entities.user import User
from infrastructure.repositories.interfaces.base import ModelRepository

TModel = TypeVar("TModel", bound=Model)

class UserRepository(ModelRepository):
    ENTITY = User
    
    @abstractmethod
    async def get_by_phone(self, phone: str) -> TModel:
        """Получить пользователя по телефону"""
        pass
