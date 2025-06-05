from fastapi import Request

from api.admin.schemas import RouteRead
from application.use_cases.base import UseCase
from application.use_cases.routes.dto import RouteFeedFiltersDTO
from domain.validators.dto import PaginatedResponse
from infrastructure.managers.paginator import Paginator
from infrastructure.uow import UnitOfWork


class RouteFeedListUseCase(UseCase):
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
        request: Request,
        filters: RouteFeedFiltersDTO,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[RouteRead]:
        add_filters = {"is_custom": False}
        async with self._uow(autocommit=True):
            result = await self._uow.routes.get_list_by_filters(filters, add_filters)

        return await Paginator(RouteRead).paginate(result, request, page, page_size)
