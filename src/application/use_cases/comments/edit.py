from datetime import datetime

from application.constants import EDIT_TIME_LIMIT, TIME_ZONE
from application.use_cases.base import UseCase
from application.use_cases.comments.dto import CommentRead, CommentTextDTO
from common.exceptions import APIException
from domain.entities.comment import Comment
from infrastructure.uow.base import UnitOfWork


class CommentEditUseCase(UseCase):
    """
    Comment edit use case.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, comment_id: int, user_id: int, data: CommentTextDTO) -> CommentRead:
        async with self._uow(autocommit=True):
            comment: Comment = await self._uow.comments.get_by_id(comment_id)
            if not comment or comment.author_id != user_id:
                raise APIException(
                    code=400,
                    message=f"Комментарий с id = {comment_id} не существует или недоступен для редактирования",
                )

            self._ensure_can_edit(comment)

            comment.comment = data.comment
            await self._uow.comments.update(comment)

            # Можно не запрашивать повторно, если update возвращает объект
            comment: Comment = await self._uow.comments.get_by_id(comment_id)
            return CommentRead.model_validate(comment)

    def _ensure_can_edit(self, comment: Comment) -> None:
        """
        Проверяет, что комментарий создан менее 24 часов назад (по UTC+5).
        """
        if not isinstance(comment.timestamp, datetime):
            raise APIException(code=500, message="Некорректный формат времени комментария")

        now_utc_plus_5 = datetime.now(TIME_ZONE)

        # Если timestamp не имеет таймзоны — локализуем его в UTC+5
        comment_time = comment.timestamp
        if comment_time.tzinfo is None:
            comment_time = comment_time.replace(tzinfo=TIME_ZONE)

        if now_utc_plus_5 - comment_time > EDIT_TIME_LIMIT:
            raise APIException(
                code=403,
                message="Редактирование комментария доступно только в течение 24 часов после публикации",
            )
