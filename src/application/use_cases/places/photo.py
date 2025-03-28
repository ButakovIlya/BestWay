from application.use_cases.base import UseCase
from application.use_cases.common.dto import ModelPhotoDTO, ObjectPhotoDTO
from application.use_cases.common.photo.photo import PhotoUpdateUseCase
from application.use_cases.places.dto import PlaceDTO
from config.exceptions import APIException
from domain.entities.place import Place
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import ModelType
from infrastructure.repositories.base import UnitOfWork


class PlacePhotoUpdateUseCase(UseCase):
    """
    Update place photo.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        storage_manager: StorageManager,
        update_photo_use_case: PhotoUpdateUseCase
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager
        self._update_photo_use_case = update_photo_use_case

    async def execute(self, place_id: int, data: ModelPhotoDTO) -> PlaceDTO:
        async with self._uow(autocommit=True):
            place: Place = await self._uow.places.get_by_id(place_id)
            if not place:
                raise APIException(code=404, message=f"Место с id={place_id} не найдено")

            photo_data = ObjectPhotoDTO(
                photo=data.photo,
                filename=data.filename,
                filepath=place.photo,
                photo_field="photo",
                model_name=ModelType.PLACES,
            )
            filepath = await self._update_photo_use_case.execute(photo_data)
            place.photo = filepath
            await self._uow.places.update(place)
            place: Place = await self._uow.places.get_by_id(place.id)

        return PlaceDTO.model_validate(place)
