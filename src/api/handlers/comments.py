from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, status

from application.use_cases.comments.dto import CommentRead
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from config.containers import Container
from domain.entities.enums import ModelType
from domain.validators.dto import PaginatedResponse

router = APIRouter()


@router.get("/", response_model=PaginatedResponse[CommentRead], status_code=status.HTTP_200_OK)
@inject
async def list_comment(
    request: Request,
    place_id: int = Query(None, ge=1),
    route_id: int = Query(None, ge=1),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: ModelObjectListUseCase = Depends(Provide[Container.object_list_use_case]),
) -> PaginatedResponse[CommentRead]:
    """Получить список комментариев с пагинацией"""
    return await use_case.execute(
        request=request,
        model_type=ModelType.COMMENTS,
        page=page,
        page_size=page_size,
        ObjectDTO=CommentRead,
        filters={"place_id": place_id, "route_id": route_id},
    )


@router.get("/{comment_id}", response_model=CommentRead, status_code=status.HTTP_200_OK)
@inject
async def retrieve_comment(
    comment_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> CommentRead:
    """Получить комментарий по ID"""
    return await use_case.execute(
        obj_id=comment_id,
        model_type=ModelType.COMMENTS,
        ObjectDTO=CommentRead,
    )
