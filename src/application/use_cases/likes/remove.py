from application.use_cases.base import UseCase
from common.exceptions import APIException
from infrastructure.uow.base import UnitOfWork


class LikeRemoveUseCase(UseCase):
    """
    Like remove use case.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, like_id: int, user_id: int) -> None:
        async with self._uow(autocommit=True):
            await self._check_if_like_exists(like_id, user_id)
            await self._uow.likes.delete_by_id(like_id)

    async def _check_if_like_exists(self, like_id: int, user_id: int) -> None:
        exists = await self._uow.likes.exists(id=like_id, author_id=user_id)
        if not exists:
            raise APIException(code=400, message=f"Лайк с id = {like_id} не существует")
