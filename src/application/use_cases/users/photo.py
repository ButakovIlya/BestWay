from application.exceptions import UserNotFound
from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserDTO, UserPhotoDTO
from domain.entities.user import User
from infrastructure.managers.base import StorageManager
from infrastructure.repositories.base import UnitOfWork

class UserPhotoUpdateUseCase(UseCase):
    """
    Update user photo.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager

    async def execute(self, user_id: int, data: UserPhotoDTO) -> UserDTO:
        async with self._uow(autocommit=True):
            user: User = await self._uow.users.get_by_id(user_id)
            if not user:
                raise UserNotFound("Пользователь не найден")

            # если передан файл, то сохраняем его в хранилище
            if data.filename:
                user_photo = user.photo
                filepath = self._storage_manager.save_user_photo(data.filename, data.photo)
                user.photo = filepath
                if user_photo:
                    self._storage_manager.delete_resource_file_by_path(user.photo)
            else:
                # если файл не передан, то удаляем его из хранилища
                if user.photo:
                    self._storage_manager.delete_resource_file_by_path(user.photo)
                    user.photo = None

            await self._uow.users.update(user)
            user: User = await self._uow.users.get_by_id(user.id)

        return UserDTO.model_validate(user)
