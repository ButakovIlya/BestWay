from io import BytesIO
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, UploadFile, status

from api.permissions.is_admin import is_admin
from application.use_cases.common.dto import ModelPhotoDTO
from application.use_cases.models.dto import ModelFieldValuesData, ModelFieldValuesInputDTO
from application.use_cases.models.field_values import ModelFieldValuesUseCase
from application.use_cases.places.photo import PlacePhotoUpdateUseCase
from config.containers import Container
from domain.entities.enums import ModelType
from infrastructure.models.alchemy.routes import Place
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.enums import RoleEnum

from .schemas import PlaceCreate, PlaceFilter, PlacePatch, PlacePut, PlaceRead


class PlaceViewSet(BaseViewSet[PlaceCreate, PlacePut, PlacePatch, PlaceRead, PlaceFilter]):
    model = Place
    schema_read = PlaceRead
    schema_create = PlaceCreate
    schema_put = PlacePut
    schema_patch = PlacePatch

    filter_schema = PlaceFilter
    ilike_list = ["name", "tags"]

    prefix = "/places"
    tags = ["Places"]

    authentication_classes = [RoleEnum.ADMIN]

    router = APIRouter(tags=tags, prefix=prefix, dependencies=[Depends(is_admin)])

    @router.post("/{place_id}/avatar", status_code=status.HTTP_200_OK)
    @inject
    async def update_avatar(
        self,
        place_id: int,
        photo: Optional[UploadFile] = File(None),
        use_case: PlacePhotoUpdateUseCase = Depends(Provide[Container.place_avatar_update_use_case]),
    ) -> PlaceRead:
        data = ModelPhotoDTO(
            photo=BytesIO(await photo.read()) if photo else None,
            filename=photo.filename if photo else None,
        )
        return await use_case.execute(place_id=place_id, data=data)

    @router.get("/field_values/{field_name}", description="Получить значения для фильтров по 'field_name'")
    @inject
    async def get_field_values(
        self,
        field_name: str,
        per_page: int = 10,
        page: int = 1,
        use_case: ModelFieldValuesUseCase = Depends(Provide[Container.model_field_values_use_case]),
    ) -> ModelFieldValuesData:
        data = ModelFieldValuesInputDTO(
            per_page=per_page,
            page=page,
            model_name=ModelType.PLACES,
            name=field_name,
        )
        return await use_case.execute(data=data)
