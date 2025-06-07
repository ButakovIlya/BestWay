from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, status

from api.handlers.comments import router as additional_router
from application.use_cases.comments.create import CommentCreateUseCase
from application.use_cases.comments.dto import CommentCreate, CommentCreateDTO, CommentRead
from application.use_cases.comments.remove import CommentRemoveUseCase
from config.containers import Container
from domain.entities.comment import Comment

router = APIRouter(tags=["Public Comments"], prefix="/comments")
router.include_router(additional_router)


@router.post("", response_model=CommentRead, status_code=status.HTTP_201_CREATED)
@inject
async def create_comment(
    request: Request,
    data: CommentCreate,
    use_case: CommentCreateUseCase = Depends(Provide[Container.comment_create_use_case]),
) -> CommentRead:
    """Создать комментарий"""
    user: Comment = request.state.user

    return await use_case.execute(
        data=CommentCreateDTO(author_id=user.id, place_id=data.place_id, route_id=data.route_id),
    )


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_comment(
    request: Request,
    comment_id: int,
    use_case: CommentRemoveUseCase = Depends(Provide[Container.remove_comment_use_case]),
) -> None:
    """Удалить комментарий"""
    user: Comment = request.state.user

    await use_case.execute(comment_id=comment_id, user_id=user.id)
