from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status

from api.handlers.posts import router as additional_router
from api.permissions.is_admin import is_admin
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from common.dto import PlacesFiltersDTO
from config.containers import Container
from domain.entities.enums import ModelType

# router = APIRouter(tags=["Posts"], prefix="/posts", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Posts"], prefix="/posts")
router.include_router(additional_router)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_post(
    post_id: int,
    use_case: ModelObjectDeleteUseCase = Depends(Provide[Container.object_delete_use_case]),
) -> Response:
    """Удалить пост"""
    await use_case.execute(
        obj_id=post_id,
        model_type=ModelType.POSTS,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
