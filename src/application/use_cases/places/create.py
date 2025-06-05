from typing import List

from application.use_cases.base import UseCase
from application.use_cases.common.dto import ModelPhotoDTO, ObjectPhotoDTO, UploadPhotosDTO
from application.use_cases.common.photo.photo import PhotoUpdateUseCase
from application.use_cases.common.photo.upload import UploadPhotosUseCase
from application.use_cases.places.dto import CreatePlaceDTO, PlaceDTO, ValidatedCreatePlaceDTO
from common.exceptions import APIException
from domain.entities.place import Place
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import ModelType
from infrastructure.uow.base import UnitOfWork


class PlaceCreateUseCase(UseCase):
    """
    Create place photo.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
        update_photo_use_case: PhotoUpdateUseCase,
        upload_photos_use_case: UploadPhotosUseCase,
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager
        self._update_photo_use_case = update_photo_use_case
        self._upload_photos_use_case = upload_photos_use_case

    async def execute(self, data: CreatePlaceDTO, user_id: int) -> PlaceDTO:
        data = self._validate_data(data)
        async with self._uow(autocommit=True):
            place: Place = await self._uow.places.create(
                Place(**data.model_dump(exclude=["photo", "photos"]))
            )

        place = await self._set_photo(photo=data.photo, place=place)
        await self._add_photos(photos=data.photos, place=place, user_id=user_id)
        return PlaceDTO.model_validate(place)

    def _validate_data(self, data: CreatePlaceDTO) -> ValidatedCreatePlaceDTO:
        validated_data = data
        if validated_data.coordinates:
            try:
                parts = data.coordinates[0].split(",")
                if len(parts) == 2:
                    parsed_coords = [float(x.strip()) for x in parts]
                    validated_data.coordinates = parsed_coords
                else:
                    raise APIException(
                        code=400, message="Координаты требуется передать в виде списка из двух float"
                    )
            except Exception:
                raise APIException(
                    code=400, message="Координаты требуется передать в виде списка из двух float"
                )

        return validated_data

    async def _set_photo(self, photo: ModelPhotoDTO, place: Place) -> Place:
        photo_data = ObjectPhotoDTO(
            photo=photo.photo,
            filename=photo.filename,
            filepath=place.photo,
            photo_field="photo",
            model_name=ModelType.PLACES,
        )
        filepath = await self._update_photo_use_case.execute(photo_data)
        place.photo = filepath
        async with self._uow(autocommit=True):
            await self._uow.places.update(place)
            place: Place = await self._uow.places.get_by_id(place.id)

        return place

    async def _add_photos(self, photos: List[ModelPhotoDTO], place: Place, user_id: int) -> None:
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
