from typing import Type

from fastapi import Request
from pydantic import BaseModel

from application.use_cases.base import UseCase
from domain.entities.enums import ModelType
from domain.validators.dto import PaginatedResponse
from infrastructure.managers.paginator import Paginator
from infrastructure.uow import UnitOfWork


class ModelObjectListUseCase(UseCase):
    """
    Get objects list.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self,
        request: Request,
        model_type: ModelType,
        ObjectDTO: Type[BaseModel],
        page: int = 1,
        page_size: int = 10,
        filters: dict = {},
    ) -> PaginatedResponse:
        async with self._uow(autocommit=True):
            repository = self._uow.get_model_repository(model_type)
            result = await repository.get_list_models(**filters)

        return await Paginator(ObjectDTO).paginate(result, request, page, page_size)
