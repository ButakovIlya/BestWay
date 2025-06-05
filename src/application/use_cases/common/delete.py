from application.use_cases.base import UseCase
from common.exceptions import APIException
from domain.entities.enums import ModelType
from infrastructure.uow import UnitOfWork


class ModelObjectDeleteUseCase(UseCase):
    """
    Use case for deleting an object by its ID and model type.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, obj_id: int, model_type: ModelType) -> bool:
        async with self._uow(autocommit=True):
            repository = self._uow.get_model_repository(model_type)

            exists = await repository.exists(id=obj_id)
            if not exists:
                raise APIException(
                    code=404, message=f"Объект {model_type.value} с id '{obj_id}' не существует"
                )

            await repository.delete_by_id(obj_id)

        return True
