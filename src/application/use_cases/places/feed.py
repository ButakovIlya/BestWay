from fastapi import Request
from pydantic import BaseModel

from application.use_cases.base import UseCase
from common.dto import PlaceRead, PlacesFiltersDTO
from domain.validators.dto import PaginatedResponse
from infrastructure.managers.paginator import Paginator
from infrastructure.uow import UnitOfWork


class PlaceFeedListUseCase(UseCase):
    """
    Get place feed.
    """

    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(
        self,
        request: Request,
        filters: PlacesFiltersDTO,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[BaseModel]:
        async with self._uow(autocommit=True):
            result = await self._uow.places.get_list_by_filters(filters)

        return await Paginator(PlaceRead).paginate(result, request, page, page_size)
