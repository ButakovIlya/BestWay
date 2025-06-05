from application.use_cases.base import UseCase
from application.use_cases.common.dto import ObjectPhotoDTO
from application.use_cases.common.photo.photo import PhotoUpdateUseCase
from application.use_cases.users.dto import UserDTO, UserPhotoDTO
from common.exceptions import APIException
from domain.entities.user import User
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import ModelType
from infrastructure.uow.base import UnitOfWork


class UserPhotoUpdateUseCase(UseCase):
    """
    Update user photo.
    """

    def __init__(
        self, uow: UnitOfWork, storage_manager: StorageManager, update_photo_use_case: PhotoUpdateUseCase
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager
        self._update_photo_use_case = update_photo_use_case

    async def execute(self, user_id: int, data: UserPhotoDTO) -> UserDTO:
        async with self._uow(autocommit=True):
            user: User = await self._uow.users.get_by_id(user_id)
            if not user:
                raise APIException(code=404, message=f"Пользователь с id={user_id} не найден")

            photo_data = ObjectPhotoDTO(
                photo=data.photo,
                filename=data.filename,
                filepath=user.photo,
                photo_field="photo",
                model_name=ModelType.USERS,
            )
            filepath = await self._update_photo_use_case.execute(photo_data)
            user.photo = filepath
            await self._uow.users.update(user)
            user: User = await self._uow.users.get_by_id(user.id)

        return UserDTO.model_validate(user)
