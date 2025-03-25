from application.exceptions import UserNotFound
from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserDTO, UserUpdateDTO
from domain.entities.user import User
from infrastructure.managers.base import StorageManager
from infrastructure.repositories.base import UnitOfWork

class UserUpdateUseCase(UseCase):
    """
    Update user info.
    """
    FIELDS_TO_SKIP_IN_DATA: list[str] = ["photo"]

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager

    async def execute(self, user_id: int, data: UserUpdateDTO) -> UserDTO:
        async with self._uow(autocommit=True):
            user: User = await self._uow.users.get_by_id(user_id)

            if not user:
                raise UserNotFound("Пользователь не найден")

            update_data = data.model_dump(exclude_unset=False)
            for key, value in update_data.items():
                if not key in self.FIELDS_TO_SKIP_IN_DATA:
                    setattr(user, key, value) 

            if data.filename:
                if user.photo:
                    self._storage_manager.delete_resource_file_by_path(user.photo)
                filepath = self._storage_manager.save_user_photo(data.filename, data.photo)
                user.photo = filepath
            
            await self._uow.users.update(user)
            user: User = await self._uow.users.get_by_id(user.id)

        return user
        return UserDTO.model_validate(user)