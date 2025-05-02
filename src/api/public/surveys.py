from typing import List

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, status

from api.permissions.is_authenticated import is_authenticated
from application.use_cases.surveys.create import SurveyCreateUseCase
from application.use_cases.surveys.delete import SurveyDeleteUseCase
from application.use_cases.surveys.dto import SurveyCreateDTO, SurveyDataUpdateDTO, SurveyDTO
from application.use_cases.surveys.list import SurveysListUseCase
from application.use_cases.surveys.retrieve import SurveyRetrieveUseCase
from application.use_cases.surveys.update import SurveyUpdateUseCase
from config.containers import Container
from domain.entities.user import User

router = APIRouter(tags=["Surveys"], prefix="/surveys")


@router.get("", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def get_surveys_list(
    request: Request, use_case: SurveysListUseCase = Depends(Provide[Container.users_survey_list_use_case])
) -> List[SurveyDTO]:
    """Эндпоинт для получения анкет пользователя."""
    user: User = request.state.user
    return await use_case.execute(user_id=user.id)


@router.get("/{survey_id}", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def get_survey(
    request: Request,
    survey_id: int,
    use_case: SurveyRetrieveUseCase = Depends(Provide[Container.user_survey_retrieve_use_case]),
) -> SurveyDTO:
    """Эндпоинт для получения анкеты пользователя."""
    user: User = request.state.user
    return await use_case.execute(survey_id=survey_id, user_id=user.id)


@router.post("", status_code=status.HTTP_201_CREATED)
@is_authenticated
@inject
async def create_survey(
    request: Request,
    data: SurveyCreateDTO,
    use_case: SurveyCreateUseCase = Depends(Provide[Container.user_survey_create_use_case]),
) -> SurveyDTO:
    """Эндпоинт для получения анкет пользователя."""
    user: User = request.state.user
    return await use_case.execute(data=data, user_id=user.id)


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
@is_authenticated
@inject
async def delete_survey(
    request: Request,
    survey_id: int,
    use_case: SurveyDeleteUseCase = Depends(Provide[Container.user_survey_delete_use_case]),
) -> None:
    """Эндпоинт для удаления анкеты пользователя."""
    user: User = request.state.user
    await use_case.execute(survey_id=survey_id, user_id=user.id)


@router.patch("/{survey_id}", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def update_survey_data(
    request: Request,
    survey_id: int,
    data: SurveyDataUpdateDTO,
    use_case: SurveyUpdateUseCase = Depends(Provide[Container.user_survey_update_use_case]),
) -> SurveyDTO:
    """Эндпоинт для редактирования анкеты пользователя."""
    user: User = request.state.user
    return await use_case.execute(survey_id=survey_id, user_id=user.id, data=data)
