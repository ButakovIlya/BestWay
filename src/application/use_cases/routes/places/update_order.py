from api.handlers.dto import RoutePlacesOrderUpdateDTO
from application.use_cases.base import UseCase
from common.exceptions import APIException
from domain.entities.place import Place
from domain.entities.route import Route
from domain.entities.route_places import RoutePlaces
from infrastructure.uow.base import UnitOfWork


class RoutePlaceUpdateOrderUseCase(UseCase):
    """
    Add route place.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, route_id: int, data: RoutePlacesOrderUpdateDTO) -> None:
        async with self._uow(autocommit=True):
            route: Route = await self._uow.routes.get_by_id(route_id)
            if not route:
                raise APIException(code=404, message=f"Маршрут с id={route_id} не найден")

            for route_place_id, order in data.order_dict.items():
                route_place: RoutePlaces = await self._uow.route_places.get_by_id(route_place_id)
                if route_place:
                    route_place.order = order
                    await self._uow.route_places.update(route_place)
