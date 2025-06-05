from pydantic import BaseModel

from application.use_cases.base import UseCase
from common.exceptions import APIException
from domain.entities.enums import ModelType
from infrastructure.uow.base import UnitOfWork


class ModelObjectUpdateUseCase(UseCase):
    """
    Full update object (PUT).
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, obj_id: int, model_type: ModelType, data: BaseModel, ObjectDTO: type[BaseModel]
    ) -> BaseModel:
        async with self._uow(autocommit=True):
            repository = self._uow.get_model_repository(model_type)
            entity = await repository.get_by_id(obj_id)
            if entity is None:
                raise APIException(code=404, message=f"Объект с id '{obj_id}' не существует")

            update_data = data.model_dump()
            for key, value in update_data.items():
                setattr(entity, key, value)

            await repository.update(entity)
            entity = await repository.get_by_id(entity.id)

        return ObjectDTO.model_validate(entity)
