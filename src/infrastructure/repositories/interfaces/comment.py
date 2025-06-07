from abc import abstractmethod
from typing import TypeVar

from application.use_cases.comments.dto import CommentBaseDTO
from domain.entities.model import Model
from infrastructure.repositories.interfaces.base import ModelRepository

TModel = TypeVar("TModel", bound=Model)


class CommentRepository(ModelRepository):
    @abstractmethod
    async def count_by_user_and_object(self, data: CommentBaseDTO) -> int:
        """Возвращает количество комментариев пользователя"""
        pass
