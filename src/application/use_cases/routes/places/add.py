from typing import List

from application.use_cases.base import UseCase
from common.exceptions import APIException
from domain.entities.place import Place
from domain.entities.route import Route
from domain.entities.route_places import RoutePlaces
from infrastructure.uow.base import UnitOfWork


class RoutePlaceAddUseCase(UseCase):
    """
    Add route place.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, route_id: int, place_id: int) -> None:
        async with self._uow(autocommit=True):
            route: Route = await self._uow.routes.get_by_id(route_id)
            if not route:
                raise APIException(code=404, message=f"Маршрут с id={route_id} не найден")

            place: Place = await self._uow.places.get_by_id(place_id)
            if not place:
                raise APIException(code=404, message=f"Место с id={route_id} не найдено")

            order = await self._uow.route_places.get_last_order_by_route_id(route_id) + 1
            route_place: RoutePlaces = await self._uow.route_places.create(
                RoutePlaces(route_id=route.id, place_id=place_id, order=order)
            )
