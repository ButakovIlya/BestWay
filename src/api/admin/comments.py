from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, Response, status

from api.permissions.is_admin import is_admin
from application.use_cases.common.create import ModelObjectCreateUseCase
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.partial_update import ModelObjectPartialUpdateUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from application.use_cases.common.update import ModelObjectUpdateUseCase
from config.containers import Container
from domain.entities.comment import Comment
from domain.entities.enums import ModelType
from domain.entities.user import User
from domain.validators.dto import PaginatedResponse

from .schemas import CommentCreateDTO, CommentPutDTO, CommentRead, CommentUpdateDTO

# router = APIRouter(tags=["Comments"], prefix="/comments", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Comments"], prefix="/comments")


@router.get("/{comment_id}", status_code=status.HTTP_200_OK)
@inject
async def retrieve_comment(
    request: Request,
    comment_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> CommentRead:
    """Получить комментарий по ID"""
    return await use_case.execute(
        obj_id=comment_id,
        model_type=ModelType.COMMENTS,
        ObjectDTO=CommentRead,
    )


@router.get("/", response_model=PaginatedResponse[CommentRead], status_code=status.HTTP_200_OK)
@inject
async def list_comments(
    request: Request,
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
    )


@router.post("", status_code=status.HTTP_200_OK)
@inject
async def create_comment(
    request: Request,
    data: CommentCreateDTO,
    use_case: ModelObjectCreateUseCase = Depends(Provide[Container.object_create_use_case]),
) -> CommentRead:
    """Создать комментарий"""
    user: User = request.state.user
    data.author_id = 6
    return await use_case.execute(
        model_type=ModelType.COMMENTS,
        data=data,
        EntityCls=Comment,
        ObjectDTO=CommentRead,
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_comment(
    comment_id: int,
    use_case: ModelObjectDeleteUseCase = Depends(Provide[Container.object_delete_use_case]),
) -> Response:
    """Удалить комментарий"""
    await use_case.execute(
        obj_id=comment_id,
        model_type=ModelType.COMMENTS,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{comment_id}", status_code=status.HTTP_200_OK)
@inject
async def partial_update_comment(
    comment_id: int,
    data: CommentUpdateDTO,
    use_case: ModelObjectPartialUpdateUseCase = Depends(Provide[Container.object_partial_update_use_case]),
) -> CommentRead:
    """Обновить комментарий частично"""
    return await use_case.execute(
        obj_id=comment_id,
        model_type=ModelType.COMMENTS,
        data=data,
        ObjectDTO=CommentRead,
    )


@router.put("/{comment_id}", status_code=status.HTTP_200_OK)
@inject
async def update_comment(
    comment_id: int,
    data: CommentPutDTO,
    use_case: ModelObjectUpdateUseCase = Depends(Provide[Container.object_update_use_case]),
) -> CommentRead:
    """Обновить комментарий полностью"""
    return await use_case.execute(
        obj_id=comment_id,
        model_type=ModelType.COMMENTS,
        data=data,
        ObjectDTO=CommentRead,
    )
