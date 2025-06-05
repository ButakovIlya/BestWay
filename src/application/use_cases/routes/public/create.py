from typing import List

from application.use_cases.routes.create import RouteCreateUseCase
from application.use_cases.routes.dto import PublicRouteCreateDTO, RouteCreateDTO, RouteDTO
from common.exceptions import APIException
from domain.entities.route import Route
from domain.entities.route_places import RoutePlaces
from domain.entities.user import User
from infrastructure.uow import UnitOfWork


class PublicRouteCreateUseCase(RouteCreateUseCase):
    """
    Create new route.
    """

    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(self, data: PublicRouteCreateDTO, user_id: int) -> RouteDTO:
        data = await self._validate_data(data)
        async with self._uow(autocommit=True):
            route: Route = await self._uow.routes.create(Route(**data.model_dump()))
            author: User = await self._uow.users.get_by_id(user_id)
            route.author = author

        return RouteDTO.model_validate(route)
