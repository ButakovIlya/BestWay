from application.constants import USERS_MAX_SURVEYS_COUNT
from application.use_cases.base import UseCase
from application.use_cases.surveys.dto import SurveyCreateDTO, SurveyDTO
from common.exceptions import APIException
from domain.entities.survey import Survey
from infrastructure.uow import UnitOfWork


class SurveyCreateUseCase(UseCase):
    """
    Create new survey.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: SurveyCreateDTO, user_id: int) -> SurveyDTO:
        async with self._uow(autocommit=True):
            if not await self.check_if_can_create(user_id):
                survey = await self._uow.surveys.create(Survey(**data.model_dump(), author_id=user_id))
            else:
                raise APIException(
                    code=400,
                    message=f"У пользователя уже есть более {USERS_MAX_SURVEYS_COUNT} анкет",
                )

        return SurveyDTO.model_validate(survey)

    async def check_if_can_create(self, user_id: int) -> bool:
        async with self._uow(autocommit=True):
            return await self._uow.surveys.get_users_surveys_count(user_id) > USERS_MAX_SURVEYS_COUNT
