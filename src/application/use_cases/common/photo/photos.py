from application.use_cases.base import UseCase
from application.use_cases.common.dto import ObjectPhotoDTO
from infrastructure.managers.base import StorageManager
from infrastructure.repositories.base import UnitOfWork


class AddPhotosUseCase(UseCase):
    """
    UseCase для сохранения/удаления фотографий объекта.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager

    async def execute(self, photos: ObjectPhotoDTO) -> str | None:
        # если передан файл, то сохраняем его в хранилище
        filepath = None
        if data.filename:
            filepath = self._storage_manager.save_photo(data.filename, data.photo, data.model_name)
        # удаляем старый файл из хранилища
        if data.filepath:
            self._storage_manager.delete_resource_file_by_path(data.filepath)

        return filepath
