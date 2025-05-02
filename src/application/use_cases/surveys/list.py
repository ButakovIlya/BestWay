from typing import List

from application.use_cases.base import UseCase
from application.use_cases.surveys.dto import SurveyDTO
from domain.entities.survey import Survey
from infrastructure.uow import UnitOfWork


class SurveysListUseCase(UseCase):
    """
    List surveys.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> List[SurveyDTO]:
        async with self._uow(autocommit=True):
            surveys: List[Survey] = await self._uow.surveys.get_list_by_user(user_id=user_id)
        return list(SurveyDTO.model_validate(survey) for survey in surveys)
