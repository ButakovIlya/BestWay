from abc import abstractmethod
from typing import List, TypeVar

from common.dto import PlacesFiltersDTO
from domain.entities.model import Model
from infrastructure.repositories.interfaces.base import ModelRepository

TModel = TypeVar("TModel", bound=Model)


class PlaceRepository(ModelRepository):
    @abstractmethod
    async def get_list_by_route_id(self, route_id: int) -> List[TModel]:
        """Получить места у маршрута"""
        pass

    @abstractmethod
    async def get_list_by_filters(self, filters: PlacesFiltersDTO) -> List[TModel]:
        """Получить места по фильтрам"""
        pass
