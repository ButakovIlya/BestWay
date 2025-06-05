from typing import Any

from pydantic import BaseModel

from application.use_cases.base import UseCase
from common.exceptions import APIException
from domain.entities.enums import ModelType
from infrastructure.uow import UnitOfWork


class ModelObjectRetrieveUseCase(UseCase):
    """
    Use case for retrieving a single object by ID and model type.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, obj_id: int, model_type: ModelType, ObjectDTO: type[BaseModel], filters: dict = {}
    ) -> BaseModel:
        async with self._uow(autocommit=True):
            repository = self._uow.get_model_repository(model_type)
            instance = await repository.get_by_id(obj_id, **filters)
            if instance is None:
                raise APIException(code=404, message=f"Объект с id '{obj_id}' не существует")

        return ObjectDTO.model_validate(instance)
