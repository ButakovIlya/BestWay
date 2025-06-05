from typing import List

from application.use_cases.base import UseCase
from application.use_cases.common.dto import ModelPhotoDTO, UploadPhotosDTO
from application.use_cases.common.photo.upload import UploadPhotosUseCase
from common.exceptions import APIException
from domain.entities.place import Place
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import ModelType
from infrastructure.uow.base import UnitOfWork


class PlacePhotosAddUseCase(UseCase):
    """
    Update place photo.
    """

    def __init__(
        self, uow: UnitOfWork, storage_manager: StorageManager, upload_photos_use_case: UploadPhotosUseCase
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager
        self._upload_photos_use_case = upload_photos_use_case

    async def execute(self, place_id: int, user_id: int, photos: List[ModelPhotoDTO]) -> None:
        async with self._uow(autocommit=True):
            place: Place = await self._uow.places.get_by_id(place_id)
            if not place:
                raise APIException(code=404, message=f"Место с id={place_id} не найдено")

            photo_data = [
                UploadPhotosDTO(
                    photo=photo.photo,
                    filename=photo.filename,
                    filepath=place.photo,
                    photo_field="photo",
                    model_name=ModelType.PLACES,
                )
                for photo in photos
            ]
            await self._upload_photos_use_case.execute(photo_data, place_id=place.id, user_id=user_id)
