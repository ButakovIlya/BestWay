from datetime import datetime

from application.use_cases.base import UseCase
from application.use_cases.surveys.dto import SurveyDTO, SurveyUpdateDTO
from common.exceptions import APIException
from domain.entities.survey import Survey
from infrastructure.uow.base import UnitOfWork


class SurveyUpdateUseCase(UseCase):
    """
    Update survey data.
    """

    def __init__(
        self,
        uow: UnitOfWork,
    ) -> None:
        self._uow = uow

    async def execute(self, user_id: int, survey_id: int, data: SurveyUpdateDTO) -> SurveyDTO:
        async with self._uow(autocommit=True):
            survey: Survey = await self._uow.surveys.get_by_user_and_id(survey_id, user_id)
            if not survey:
                raise APIException(code=404, message=f"Анкеты с id '{survey_id}' не существует")

            validated_data = self._validate_data(data).model_dump(exclude_unset=True)
            if "name" in validated_data:
                survey.name = validated_data["name"]
            if "city" in validated_data:
                survey.city = validated_data["city"]
            if "data" in validated_data:
                survey.data = validated_data["data"]
            if "places" in validated_data:
                await self._validate_places(data)
                survey.places = validated_data["places"]

            survey.updated_at = datetime.now()
            await self._uow.surveys.update(survey)
            survey: Survey = await self._uow.surveys.get_by_id(survey.id)

        return SurveyDTO.model_validate(survey)

    @staticmethod
    def _validate_data(data: SurveyUpdateDTO) -> SurveyUpdateDTO:
        data = SurveyUpdateDTO.model_validate(data)
        return data

    async def _validate_places(self, data: SurveyUpdateDTO) -> None:
        for _, place_data in data.places.items():
            if place_data.place_id is not None:
                place_exists = await self._uow.places.exists(id=place_data.place_id)
                if not place_exists:
                    raise APIException(code=400, message=f"Место с id={place_data.place_id} не существует")
