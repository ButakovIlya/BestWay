from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserDTO
from config.exceptions import APIException
from infrastructure.uow import UnitOfWork


class UserRetrieveUseCase(UseCase):
    """
    Retrieve user.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> UserDTO:
        async with self._uow(autocommit=True):
            try:
                user = await self._uow.users.get_by_id(user_id)
            except ValueError:
                raise APIException(code=404, message=f"Пользователь с id '{user_id}' не существует")

        return UserDTO.model_validate(user)
