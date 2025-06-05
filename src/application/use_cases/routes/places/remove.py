from application.use_cases.base import UseCase
from common.exceptions import APIException
from domain.entities.place import Place
from domain.entities.route import Route
from infrastructure.uow.base import UnitOfWork


class RoutePlaceRemoveUseCase(UseCase):
    """
    Add route place.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, route_id: int, route_place_id: int | None) -> None:
        async with self._uow(autocommit=True):
            route: Route = await self._uow.routes.get_by_id(route_id)
            if not route:
                raise APIException(code=404, message=f"Маршрут с id={route_id} не найден")

            if route_place_id:
                place: Place = await self._uow.route_places.get_by_id(route_place_id)
                if not place:
                    raise APIException(code=404, message=f"Место с id={route_place_id} не найдено")

            await self._uow.route_places.remove_route_place_by_id(route_id, route_place_id)
