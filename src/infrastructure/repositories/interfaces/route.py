from abc import abstractmethod
from typing import Any, List

from sqlalchemy import Result

from application.use_cases.routes.dto import RouteFeedFiltersDTO
from domain.entities.route import Route
from infrastructure.repositories.interfaces.base import ModelRepository


class RouteRepository(ModelRepository):
    @abstractmethod
    async def get_by_id(self, model_id: int, **filters: Any) -> Route:
        """Получить маршрут по id"""
        pass

    @abstractmethod
    async def get_list_by_filters(self, filters: RouteFeedFiltersDTO, add_filters: Any) -> Result:
        """Получить маршруты по фильтрам"""
        pass

    @abstractmethod
    async def get_list_models(self) -> List[Any]:
        """Получить список маршрутов"""
        pass
