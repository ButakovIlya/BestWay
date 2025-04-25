from application.use_cases.base import UseCase
from domain.entities.photo import Photo
from infrastructure.managers.base import StorageManager
from infrastructure.repositories.base import UnitOfWork


class DeletePhotoUseCase(UseCase):
    """
    UseCase для удаления фотографии объекта.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager

    async def execute(
        self, photo_id: int, place_id: int | None = None, route_id: int | None = None
    ) -> None:
        async with self._uow(autocommit=True):
            photo: Photo = await self._uow.photos.get_by_id(model_id=photo_id)
            await self._uow.photos.delete_by_id(model_id=photo_id)

        filepath = photo.url
        if filepath:
            self._storage_manager.delete_resource_file_by_path(filepath)

        return None
