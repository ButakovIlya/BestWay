from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, status

from api.handlers.likes import router as additional_router
from application.use_cases.likes.create import LikeCreateUseCase
from application.use_cases.likes.dto import LikeCreate, LikeCreateDTO, LikeRead
from application.use_cases.likes.remove import LikeRemoveUseCase
from config.containers import Container
from domain.entities.like import Like

router = APIRouter(tags=["Public Likes"], prefix="/likes")
router.include_router(additional_router)


@router.post("", response_model=LikeRead, status_code=status.HTTP_201_CREATED)
@inject
async def create_like(
    request: Request,
    data: LikeCreate,
    use_case: LikeCreateUseCase = Depends(Provide[Container.like_create_use_case]),
) -> LikeRead:
    """Создать лайк"""
    user: Like = request.state.user

    return await use_case.execute(
        data=LikeCreateDTO(
            author_id=user.id,
            place_id=data.place_id,
            route_id=data.route_id,
            post_id=data.post_id,
        ),
    )


@router.delete("/{like_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def remove_like(
    request: Request,
    like_id: int,
    use_case: LikeRemoveUseCase = Depends(Provide[Container.remove_like_use_case]),
) -> None:
    """Удалить лайк"""
    user: Like = request.state.user

    await use_case.execute(like_id=like_id, user_id=user.id)
