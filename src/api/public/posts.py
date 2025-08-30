from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, Response, status

from api.admin.schemas import PostRead
from api.handlers.posts import router as additional_router
from api.permissions.is_admin import is_admin
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from application.use_cases.places.feed import PlaceFeedListUseCase
from common.dto import PlacesFiltersDTO
from config.containers import Container
from domain.entities.enums import ModelType
from domain.validators.dto import PaginatedResponse

router = APIRouter(tags=["Public Post"], prefix="/posts")

router.include_router(additional_router)


@router.get("/my", response_model=PaginatedResponse[PostRead], status_code=status.HTTP_200_OK)
@inject
async def list_my_posts(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: ModelObjectListUseCase = Depends(Provide[Container.object_list_use_case]),
) -> PaginatedResponse[PostRead]:
    """Получить список постов"""
    return await use_case.execute(
        request=request,
        model_type=ModelType.POSTS,
        page=page,
        page_size=page_size,
        ObjectDTO=PostRead,
        filters={"author_id": request.state.user.id},
    )


@router.get("/my/{post_id}", response_model=PostRead, status_code=status.HTTP_200_OK)
@inject
async def retrieve_my_post(
    request: Request,
    post_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> PostRead:
    """Получить пост по ID"""
    return await use_case.execute(
        obj_id=post_id,
        model_type=ModelType.POSTS,
        ObjectDTO=PostRead,
        filters={"author_id": request.state.user.id},
    )


@router.delete("/my/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_my_post(
    request: Request,
    post_id: int,
    use_case: ModelObjectDeleteUseCase = Depends(Provide[Container.object_delete_use_case]),
) -> Response:
    """Удалить пост"""
    await use_case.execute(obj_id=post_id, model_type=ModelType.POSTS, author_id=request.state.user.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
