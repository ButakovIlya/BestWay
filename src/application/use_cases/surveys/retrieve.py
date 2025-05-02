from application.use_cases.base import UseCase
from application.use_cases.surveys.dto import SurveyDTO
from common.exceptions import APIException
from infrastructure.uow import UnitOfWork


class SurveyRetrieveUseCase(UseCase):
    """
    Retrieve survey
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, survey_id: int, user_id: int) -> SurveyDTO:
        async with self._uow(autocommit=True):
            try:
                survey = await self._uow.surveys.get_by_id(survey_id)
                if not survey.author_id == user_id:
                    raise APIException(code=404, message=f"Анткета с id '{survey}' не существует")
            except ValueError:
                raise APIException(code=404, message=f"Анткета с id '{survey}' не существует")

        return SurveyDTO.model_validate(survey)
