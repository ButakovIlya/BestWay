from api.admin.schemas import RouteRead
from application.use_cases.base import UseCase
from infrastructure.uow import UnitOfWork


class RouteFeedRetrieveUseCase(UseCase):
    """
    Get route feed.
    """

    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(
        self,
        route_id: int,
    ) -> RouteRead:
        async with self._uow(autocommit=True):
            filters = {"is_custom": False}
            route = await self._uow.routes.get_by_id(route_id, **filters)
        return RouteRead.model_validate(route)
