from abc import abstractmethod
from typing import TypeVar

from application.use_cases.likes.dto import LikeDTO
from domain.entities.model import Model
from infrastructure.repositories.interfaces.base import ModelRepository

TModel = TypeVar("TModel", bound=Model)


class LikeRepository(ModelRepository):
    @abstractmethod
    async def check_if_user_has_like(self, data: LikeDTO) -> bool:
        """Проверяет, существует ли лайк"""
        pass
