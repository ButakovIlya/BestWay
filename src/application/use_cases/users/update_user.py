from application.exceptions import UserNotFound
from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserDTO, UserUpdateDTO
from config.exceptions import APIException
from domain.entities.user import User
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import UserFileFiels
from infrastructure.repositories.base import UnitOfWork


class UserUpdateUseCase(UseCase):
    """
    Update user info.
    """

    FIELDS_TO_SKIP_IN_DATA: list[str] = [field.value for field in UserFileFiels]

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager

    async def execute(self, user_id: int, data: UserUpdateDTO) -> UserDTO:
        async with self._uow(autocommit=True):
            try:
                user: User = await self._uow.users.get_by_id(user_id)
            except ValueError:
                raise APIException(code=404, message=f"Пользователь с id '{user_id}' не существует")

            if not user:
                raise UserNotFound("Пользователь не найден")

            update_data = data.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                if key not in self.FIELDS_TO_SKIP_IN_DATA:
                    setattr(user, key, value)

            await self._uow.users.update(user)
            user: User = await self._uow.users.get_by_id(user.id)

        return UserDTO.model_validate(user)
