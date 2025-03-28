from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status

from api.permissions.is_admin import is_admin
from application.use_cases.common import PhotoUpdateUseCase
from config.containers import Container
from infrastructure.models.alchemy.routes import Place
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.decorators import has_roles
from infrastructure.permissions.enums import RoleEnum

from .schemas import PlaceCreate, PlacePatch, PlacePut, PlaceRead


class PlaceViewSet(BaseViewSet[PlaceCreate, PlacePut, PlacePatch, PlaceRead]):
    model = Place
    schema_read = PlaceRead
    schema_create = PlaceCreate
    schema_put = PlacePut
    schema_patch = PlacePatch
    prefix = "/places"
    tags = ["Places"]

    authentication_classes = [RoleEnum.ADMIN]

    router = APIRouter(tags=tags, prefix=prefix, dependencies=[Depends(is_admin)])

    @router.post("/{place_id}/avatar", status_code=status.HTTP_200_OK)
    @inject
    async def update_avatar(
        place_id: int,
        use_case: PhotoUpdateUseCase = Depends(Provide[Container.update_photo_use_case]),
    ) -> Response:
        return Response(status_code=200)
