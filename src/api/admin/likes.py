from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status

from api.handlers.likes import router as additional_router
from api.permissions.is_admin import is_admin
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from config.containers import Container
from domain.entities.enums import ModelType

# router = APIRouter(tags=["Likes"], prefix="/likes", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Likes"], prefix="/likes")
router.include_router(additional_router)


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
