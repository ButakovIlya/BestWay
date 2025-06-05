from typing import List

from application.use_cases.base import UseCase
from application.use_cases.common.dto import ModelPhotoDTO, UploadPhotosDTO
from application.use_cases.common.photo.upload import UploadPhotosUseCase
from common.exceptions import APIException
from domain.entities.route import Route
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import ModelType
from infrastructure.uow.base import UnitOfWork


class RoutePhotosAddUseCase(UseCase):
    """
    Update route photo.
    """

    def __init__(
        self, uow: UnitOfWork, storage_manager: StorageManager, upload_photos_use_case: UploadPhotosUseCase
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager
        self._upload_photos_use_case = upload_photos_use_case

    async def execute(self, route_id: int, user_id: int, photos: List[ModelPhotoDTO]) -> None:
        async with self._uow(autocommit=True):
            route: Route = await self._uow.routes.get_by_id(route_id)
            if not route:
                raise APIException(code=404, message=f"Место с id={route_id} не найдено")

            photo_data = [
                UploadPhotosDTO(
                    photo=photo.photo,
                    filename=photo.filename,
                    filepath=route.photo,
                    photo_field="photo",
                    model_name=ModelType.ROUTES,
                )
                for photo in photos
            ]
            await self._upload_photos_use_case.execute(photo_data, route_id=route.id, user_id=user_id)
