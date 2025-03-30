from application.use_cases.base import UseCase
from application.use_cases.models.dto import ModelFieldValuesData, ModelFieldValuesInputDTO
from infrastructure.uow.base import UnitOfWork


class ModelFieldValuesUseCase(UseCase):
    """
    Return list of model field values.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: ModelFieldValuesInputDTO) -> ModelFieldValuesData:
        page = data.page
        per_page = data.per_page
        name = data.name

        async with self._uow(autocommit=True):
            repository = self._uow.get_model_repository(data.model_name.value)
            model_data = await repository.get_field_values(
                per_page=per_page,
                page=page,
                name=name,
            )
            total_rows = await repository.total_rows_for_values(
                name=data.name,
            )

        next_page = page + 1 if page and per_page and page * per_page < total_rows else None
        previous_page = page - 1 if page and page > 1 else None
        return ModelFieldValuesData(
            results=model_data,
            count=total_rows,
            next=next_page,
            previous=previous_page,
        )
