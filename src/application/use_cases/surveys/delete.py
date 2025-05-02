from application.use_cases.base import UseCase
from common.exceptions import APIException
from infrastructure.uow import UnitOfWork


class SurveyDeleteUseCase(UseCase):
    """
    Delete survey.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, survey_id: int, user_id: int) -> bool:
        async with self._uow(autocommit=True):
            if await self._uow.surveys.exists(id=survey_id, author_id=user_id):
                await self._uow.surveys.delete_by_id(survey_id)
            else:
                raise APIException(code=404, message=f"Анкета с id '{survey_id}' не существует")

        return True
