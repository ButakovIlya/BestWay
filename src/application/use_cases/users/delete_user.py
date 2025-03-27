from application.use_cases.base import UseCase
from config.exceptions import APIException
from infrastructure.uow import UnitOfWork


class UserDeleteUseCase(UseCase):
    """
    Delete user.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> bool:
        async with self._uow(autocommit=True):
            if await self._uow.users.exists(user_id):
                await self._uow.users.delete_by_id(user_id)
            else:
                raise APIException(code=404, message=f"Пользователь с id '{user_id}' не существует")

        return True
