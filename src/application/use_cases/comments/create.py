from application.constants import USERS_MAX_COMMENTS_COUNT
from application.use_cases.base import UseCase
from application.use_cases.comments.dto import CommentCreateDTO, CommentRead
from common.exceptions import APIException
from domain.entities.comment import Comment
from infrastructure.uow.base import UnitOfWork


class CommentCreateUseCase(UseCase):
    """
    Comment object use case.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: CommentCreateDTO) -> CommentRead:
        async with self._uow(autocommit=True):
            await self._validate_data(data)
            await self._check_if_comment_limit_exceeded(data)
            comment: Comment = await self._uow.comments.create(Comment(**data.model_dump()))
            return CommentRead.model_validate(comment)

    async def _validate_data(self, data: CommentCreateDTO) -> None:
        if not data.place_id and not data.route_id and not data.post_id:
            raise APIException(
                code=400,
                message="Одновременно поля 'post_id', 'place_id' и 'route_id' не могут быть пустыми",
            )
        if data.place_id and data.route_id:
            raise APIException(code=400, message="Нельзя одновременно передать 'place_id' и 'route_id'")

        if data.place_id:
            exists = await self._uow.places.exists(id=data.place_id)
            if not exists:
                raise APIException(code=400, message=f"Место с id = '{data.place_id}' не существует")

        if data.route_id:
            exists = await self._uow.routes.exists(id=data.route_id)
            if not exists:
                raise APIException(code=400, message=f"Маршрут с id = '{data.route_id}' не существует")

    async def _check_if_comment_limit_exceeded(self, data: CommentCreateDTO) -> None:
        comments_count = await self._uow.comments.count_by_user_and_object(data=data)
        if comments_count > USERS_MAX_COMMENTS_COUNT:
            raise APIException(
                code=400,
                message=f"У пользователя уже есть более {USERS_MAX_COMMENTS_COUNT} комментариев",
            )
