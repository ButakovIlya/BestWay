from typing import List

from application.use_cases.base import UseCase
from application.use_cases.routes.dto import RouteCreateDTO, RouteDTO
from common.exceptions import APIException
from domain.entities.route import Route
from domain.entities.route_places import RoutePlaces
from infrastructure.uow import UnitOfWork


class RouteCreateUseCase(UseCase):
    """
    Create new route.
    """

    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(self, data: RouteCreateDTO) -> RouteDTO:
        # data = await self._validate_data(data)
        async with self._uow(autocommit=True):
            # places = data.places
            route: Route = await self._uow.routes.create(
                Route(**data.model_dump(exclude=["places", "photo", "photos"]))
            )
            # author: User = await self._uow.users.get_by_id(data.author_id)
            # route.author = author

        # async with self._uow(autocommit=True):
        #     route = await self._add_places(route, places)

        return RouteDTO.model_validate(route)

    # async def _validate_data(self, data: RouteCreateDTO) -> RouteCreateDTO:
    #     validated_data = data
    #     if data.places:
    #         async with self._uow(autocommit=True):
    #             places = data.places
    #             exists = await self._uow.places.all_exist_by_id_list(id_lst=places)
    #             if not exists:
    #                 raise APIException(
    #                     code=400,
    #                     message=f"Не найдены некоторые места для добавления в маршрут: {validated_data}",
    #                 )

    #     return validated_data

    # async def _add_places(self, route: Route, places: List[int] = []) -> Route:
    #     if places:
    #         async with self._uow(autocommit=True):
    #             places = await self._uow.places.get_list_by_ids(places)
    #             route_places = [
    #                 RoutePlaces(route_id=route.id, place_id=place.id, order=order)
    #                 for order, place in enumerate(places, 1)
    #             ]
    #             route_places = await self._uow.route_places.bulk_create(route_places)

    #     return route
