from abc import abstractmethod

from domain.entities.route_places import RoutePlaces
from infrastructure.repositories.interfaces.base import ModelRepository


class RoutePlacesRepository(ModelRepository):
    @abstractmethod
    async def get_last_order_by_route_id(self, route_id: int) -> int:
        """Получить порядок последнего места маршрута"""
        pass

    @abstractmethod
    async def remove_route_place_by_id(self, route_id: int, route_place_id: int | None) -> bool:
        """Удалить место из маршрута или очистить список мест"""
        pass

    @abstractmethod
    async def copy(self, route_id: int, places: list[RoutePlaces]) -> list[RoutePlaces]:
        """Скопировать места маршрута из маршрута"""
        pass
