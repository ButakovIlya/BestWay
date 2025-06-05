from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, Response, status

from api.permissions.is_admin import is_admin
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from config.containers import Container
from domain.entities.enums import ModelType
from domain.validators.dto import PaginatedResponse

from .schemas import SurveyRead

# router = APIRouter(tags=["Surveys"], prefix="/surveys", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Surveys"], prefix="/surveys")


@router.get("/", response_model=PaginatedResponse[SurveyRead], status_code=status.HTTP_200_OK)
@inject
async def list_surveys(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: ModelObjectListUseCase = Depends(Provide[Container.object_list_use_case]),
) -> PaginatedResponse[SurveyRead]:
    """Получить список опросов"""
    return await use_case.execute(
        request=request,
        model_type=ModelType.SURVEYS,
        page=page,
        page_size=page_size,
        ObjectDTO=SurveyRead,
    )


@router.get("/{survey_id}", response_model=SurveyRead, status_code=status.HTTP_200_OK)
@inject
async def retrieve_survey(
    survey_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> SurveyRead:
    """Получить опрос по ID"""
    return await use_case.execute(
        obj_id=survey_id,
        model_type=ModelType.SURVEYS,
        ObjectDTO=SurveyRead,
    )


@router.delete("/{survey_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_survey(
    survey_id: int,
    use_case: ModelObjectDeleteUseCase = Depends(Provide[Container.object_delete_use_case]),
) -> Response:
    """Удалить опрос"""
    await use_case.execute(
        obj_id=survey_id,
        model_type=ModelType.SURVEYS,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
