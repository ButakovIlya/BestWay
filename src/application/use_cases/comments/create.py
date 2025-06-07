from application.use_cases.base import UseCase
from application.use_cases.likes.dto import CommentCreateDTO, CommentRead
from common.exceptions import APIException
from domain.entities.like import Comment
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
            await self._check_if_like_exists(data)
            like: Comment = await self._uow.likes.create(Comment(**data.model_dump()))
            return CommentRead.model_validate(like)

    async def _validate_data(self, data: CommentCreateDTO) -> None:
        if not data.place_id and not data.route_id:
            raise APIException(code=400, message="Оба поля 'place_id' и 'route_id' не могут быть пустыми")
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

    async def _check_if_like_exists(self, data: CommentCreateDTO) -> None:
        exists = await self._uow.likes.check_if_user_has_like(data=data)
        if exists:
            raise APIException(
                code=400, message=f"Лайк с такими данными уже существует: {data.model_dump()}"
            )
