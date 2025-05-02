from datetime import datetime

from application.use_cases.base import UseCase
from application.use_cases.surveys.dto import SurveyDataUpdateDTO, SurveyDTO
from common.exceptions import APIException
from domain.entities.survey import Survey
from infrastructure.repositories.base import UnitOfWork


class SurveyUpdateUseCase(UseCase):
    """
    Update survey data.
    """

    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(self, user_id: int, survey_id: int, data: SurveyDataUpdateDTO) -> SurveyDTO:
        async with self._uow(autocommit=True):
            survey: Survey = await self._uow.surveys.get_by_user_and_id(survey_id, user_id)
            if not survey:
                raise APIException(code=404, message=f"Анкеты с id '{survey_id}' не существует")

            validated_data = self._validate_data(data)
            survey.data = validated_data.model_dump(mode="json", exclude_none=True)
            survey.updated_at = datetime.now()
            await self._uow.surveys.update(survey)
            survey: Survey = await self._uow.surveys.get_by_id(survey.id)

        return SurveyDTO.model_validate(survey)

    @staticmethod
    def _validate_data(data: SurveyDataUpdateDTO) -> SurveyDataUpdateDTO:
        return SurveyDataUpdateDTO.model_validate(data)
