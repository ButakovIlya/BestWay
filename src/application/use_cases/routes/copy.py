from openai import BaseModel

from application.use_cases.base import UseCase
from infrastructure.uow import UnitOfWork


class RouteCopyUseCase(UseCase):
    """
    Create new route.
    """

    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(self, route_id: int, user_id: int, dto: BaseModel) -> BaseModel:
        async with self._uow(autocommit=True):
            destination_route = await self._uow.routes.get_by_id(route_id)
            my_route = await self._uow.routes.copy(destination_route, user_id)
            my_route.places = await self._uow.route_places.copy(
                my_route.id,
                destination_route.places,
            )

        return dto.model_validate(my_route)
