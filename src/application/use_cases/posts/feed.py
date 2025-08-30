from fastapi import Request
from openai import BaseModel

from application.use_cases.base import UseCase
from common.dto import PostsFiltersDTO
from domain.entities.post import Post
from domain.validators.dto import PaginatedResponse
from infrastructure.managers.paginator import Paginator
from infrastructure.uow.base import UnitOfWork


class PostFeedFilterUseCase(UseCase):
    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(
        self,
        request: Request,
        filters: PostsFiltersDTO,
        PaginatorModel: BaseModel,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[BaseModel]:
        async with self._uow(autocommit=True):
            result = await self._uow.posts.get_list_by_filters(filters)

        return await Paginator(PaginatorModel).paginate(result, request, page, page_size)
