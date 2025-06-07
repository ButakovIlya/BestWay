from pydantic import BaseModel

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
        PaginatorModel: BaseModel,
    ) -> BaseModel:
        async with self._uow(autocommit=True):
            filters = {"is_custom": False}
            route = await self._uow.routes.get_by_id(route_id, **filters)
        return PaginatorModel.model_validate(route)
