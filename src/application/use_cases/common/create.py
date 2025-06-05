from pydantic import BaseModel

from application.use_cases.base import UseCase
from domain.entities.entity import Entity
from domain.entities.enums import ModelType
from infrastructure.uow import UnitOfWork


class ModelObjectCreateUseCase(UseCase):
    """
    Create a new object of the given model type.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(
        self, model_type: ModelType, data: BaseModel, EntityCls: type[Entity], ObjectDTO: type[BaseModel]
    ) -> BaseModel:
        async with self._uow(autocommit=True):
            repository = self._uow.get_model_repository(model_type)
            instance = await repository.create(EntityCls(**data.model_dump()))

        return ObjectDTO.model_validate(instance)
