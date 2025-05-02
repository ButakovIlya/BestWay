from application.use_cases.base import UseCase
from application.use_cases.common.dto import ModelPhotoDTO, ObjectPhotoDTO
from application.use_cases.common.photo.photo import PhotoUpdateUseCase
from application.use_cases.routes.dto import RouteDTO
from common.exceptions import APIException
from domain.entities.route import Route
from infrastructure.managers.base import StorageManager
from infrastructure.managers.enum import ModelType
from infrastructure.repositories.base import UnitOfWork


class RoutePhotoUpdateUseCase(UseCase):
    """
    Update route photo.
    """

    def __init__(
        self, uow: UnitOfWork, storage_manager: StorageManager, update_photo_use_case: PhotoUpdateUseCase
    ) -> None:
        self._uow = uow
        self._storage_manager = storage_manager
        self._update_photo_use_case = update_photo_use_case

    async def execute(self, route_id: int, data: ModelPhotoDTO) -> RouteDTO:
        async with self._uow(autocommit=True):
            route: Route = await self._uow.routes.get_by_id(route_id)
            if not route:
                raise APIException(code=404, message=f"Маршрут с id={route_id} не найден")

            photo_data = ObjectPhotoDTO(
                photo=data.photo,
                filename=data.filename,
                filepath=route.photo,
                photo_field="photo",
                model_name=ModelType.ROUTES,
            )
            filepath = await self._update_photo_use_case.execute(photo_data)
            route.photo = filepath
            await self._uow.routes.update(route)
            route: Route = await self._uow.routes.get_by_id(route.id)

        return RouteDTO.model_validate(route)
