from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, Response, status

from api.permissions.is_admin import is_admin
from application.use_cases.common.create import ModelObjectCreateUseCase
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from config.containers import Container
from domain.entities.enums import ModelType
from domain.entities.like import Like
from domain.validators.dto import PaginatedResponse

from .schemas import LikeCreate, LikeRead

# router = APIRouter(tags=["Likes"], prefix="/likes", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Likes"], prefix="/likes")


@router.get("/", response_model=PaginatedResponse[LikeRead], status_code=status.HTTP_200_OK)
@inject
async def list_likes(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: ModelObjectListUseCase = Depends(Provide[Container.object_list_use_case]),
) -> PaginatedResponse[LikeRead]:
    """Получить список лайков с пагинацией"""
    return await use_case.execute(
        request=request,
        model_type=ModelType.LIKES,
        page=page,
        page_size=page_size,
        ObjectDTO=LikeRead,
    )


@router.get("/{like_id}", response_model=LikeRead, status_code=status.HTTP_200_OK)
@inject
async def retrieve_like(
    request: Request,
    like_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> LikeRead:
    """Получить лайк по ID"""
    return await use_case.execute(
        obj_id=like_id,
        model_type=ModelType.LIKES,
        ObjectDTO=LikeRead,
    )


@router.post("", response_model=LikeRead, status_code=status.HTTP_201_CREATED)
@inject
async def create_like(
    request: Request,
    data: LikeCreate,
    use_case: ModelObjectCreateUseCase = Depends(Provide[Container.object_create_use_case]),
) -> LikeRead:
    """Создать лайк"""
    user: Like = request.state.user
    data.author_id = 6
    return await use_case.execute(
        model_type=ModelType.LIKES,
        data=data,
        EntityCls=Like,
        ObjectDTO=LikeRead,
    )


@router.delete("/{like_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_like(
    like_id: int,
    use_case: ModelObjectDeleteUseCase = Depends(Provide[Container.object_delete_use_case]),
) -> Response:
    """Удалить лайк"""
    await use_case.execute(
        obj_id=like_id,
        model_type=ModelType.LIKES,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
