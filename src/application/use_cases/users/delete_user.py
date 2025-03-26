from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserCreateDTO, UserDTO, UserDeleteDTO
from config.exceptions import APIException
from domain.entities.user import User
from infrastructure.uow import UnitOfWork


class UserDeleteUseCase(UseCase):
    """
    Delete user.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, phone: str) -> bool:
        async with self._uow(autocommit=True):
            if await self._uow.users.exists_by_phone(phone):
                await self._uow.users.delete_by_phone(phone)
            else:
                raise APIException(
                    code=404,
                    message=f"Пользователь с номером '{phone}' не существует"
                )

        return True
