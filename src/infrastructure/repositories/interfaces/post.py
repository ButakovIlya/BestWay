from abc import abstractmethod
from typing import Any, List, TypeVar

from domain.entities.model import Model
from domain.entities.post import Post
from infrastructure.repositories.interfaces.base import ModelRepository

TModel = TypeVar("TModel", bound=Model)


class PostRepository(ModelRepository):
    @abstractmethod
    async def get_by_id(self, model_id: int, **filters: Any) -> Post:
        """Получить маршрут по id"""
        pass

    @abstractmethod
    async def get_list_models(self) -> List[Any]:
        """Получить список маршрутов"""
        pass
