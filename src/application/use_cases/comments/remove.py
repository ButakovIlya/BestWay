from application.use_cases.base import UseCase
from common.exceptions import APIException
from infrastructure.uow.base import UnitOfWork


class CommentRemoveUseCase(UseCase):
    """
    Comment remove use case.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, comment_id: int, user_id: int) -> None:
        async with self._uow(autocommit=True):
            await self._check_if_comment_exists(comment_id, user_id)
            await self._uow.comments.delete_by_id(comment_id)

    async def _check_if_comment_exists(self, comment_id: int, user_id: int) -> None:
        exists = await self._uow.comments.exists(id=comment_id, author_id=user_id)
        if not exists:
            raise APIException(code=400, message=f"Комментарий с id = {comment_id} не существует")
