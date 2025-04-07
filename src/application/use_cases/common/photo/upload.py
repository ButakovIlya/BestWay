from typing import List

from application.use_cases.base import UseCase
from application.use_cases.common.dto import UploadPhotosDTO
from domain.entities.photo import Photo
from infrastructure.managers.base import StorageManager
from infrastructure.repositories.base import UnitOfWork


class UploadPhotosUseCase(UseCase):
    """
    UseCase для сохранения/удаления списка фотографий объекта.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager

    async def execute(self, photos: List[UploadPhotosDTO], place_id: int, user_id: int) -> str | None:

        photos_to_create: List[Photo] = []
        for photo in photos:
            photo_data = Photo(place_id=place_id, uploaded_by=user_id)
            filepath = None
            if photo.filename:
                filepath = self._storage_manager.save_photo(photo.filename, photo.photo, photo.model_name)

            photo_data.url = filepath
            photos_to_create.append(photo_data)

        async with self._uow(autocommit=True):
            await self._uow.photos.bulk_create(data=photos_to_create)
