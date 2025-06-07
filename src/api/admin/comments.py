from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status

from api.handlers.comments import router as additional_router
from api.permissions.is_admin import is_admin
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from config.containers import Container
from domain.entities.enums import ModelType

# router = APIRouter(tags=["Comments"], prefix="/comments", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Comments"], prefix="/comments")
router.include_router(additional_router)


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
