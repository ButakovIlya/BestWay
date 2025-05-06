from io import BytesIO
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from sqlalchemy import Select, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.permissions.is_admin import is_admin
from application.use_cases.common.dto import ModelPhotoDTO
from application.use_cases.common.photo.delete import DeletePhotoUseCase
from application.use_cases.models.dto import ModelFieldValuesData, ModelFieldValuesInputDTO
from application.use_cases.models.field_values import ModelFieldValuesUseCase
from application.use_cases.models.select_field_values import SelectFieldValuesUseCase
from application.use_cases.places.add_photos import PlacePhotosAddUseCase
from application.use_cases.places.avatar import PlacePhotoUpdateUseCase
from application.use_cases.places.create import PlaceCreateUseCase
from application.use_cases.places.dto import CreatePlaceDTO
from config.containers import Container
from domain.entities.enums import CityCategory, ModelType, PlaceCategory, PlaceType
from infrastructure.models.alchemy.routes import Place
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.enums import RoleEnum
from src.common.exceptions import APIException

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

    allowed_methods: list[str] = ["list", "get", "create", "put", "patch", "delete", "options"]

    authentication_classes = [RoleEnum.ADMIN]

    router = APIRouter(tags=tags, prefix=prefix, dependencies=[Depends(is_admin)])

    def build_select_stmt(self, item_id: Optional[int] = None, filters: Optional[dict] = None) -> Select:
        stmt = (
            super().build_select_stmt(item_id=item_id, filters=filters).options(selectinload(Place.photos))
        )
        return stmt

    @router.post("/", status_code=status.HTTP_200_OK)
    @inject
    async def create(
        self,
        request: Request,
        name: str = Form(...),
        category: PlaceCategory = Form(...),
        city: Optional[CityCategory] = Form(None),
        type: Optional[PlaceType] = Form(None),
        tags: Optional[str] = Form(None),
        coordinates: Optional[List[str]] = Form(
            None,
            description="Введите координаты в формате: 15.5,14.6",
        ),
        map_name: Optional[str] = Form(None),
        photo: Optional[UploadFile] = File(None),
        photos: Optional[List[UploadFile]] = File(None),
        use_case: PlaceCreateUseCase = Depends(Provide[Container.create_place_use_case]),
    ):
        photo_data = ModelPhotoDTO(
            photo=BytesIO(await photo.read()) if photo else None,
            filename=photo.filename if photo else None,
        )
        photos_data = (
            [
                ModelPhotoDTO(
                    photo=BytesIO(await photo.read()) if photo else None,
                    filename=photo.filename if photo else None,
                )
                for photo in photos
            ]
            if photos
            else []
        )

        data = CreatePlaceDTO(
            name=name,
            city=city,
            type=type,
            tags=tags,
            category=category,
            coordinates=coordinates,
            map_name=map_name,
            photo=photo_data,
            photos=photos_data,
        )
        user_id: int = request.state.user.id
        return await use_case.execute(data=data, user_id=user_id)

    @router.patch("/{item_id}", response_model=PlaceRead)
    @inject
    async def patch(
        self,
        item_id: int,
        item_data: PlacePatch,
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> PlaceRead:
        try:
            values = item_data.model_dump(exclude_unset=True)
            if not values:
                raise APIException(code=400, message="Нет данных для обновления")

            stmt = (
                update(self.model)
                .where(self.model.id == item_id)
                .values(**values)
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(stmt)
            await session.commit()

            result = await session.execute(
                select(self.model).where(self.model.id == item_id).options(selectinload(Place.photos))
            )
            db_obj = result.scalar_one_or_none()

            if not db_obj:
                raise APIException(code=404, message="Item not found")

            return db_obj
        finally:
            await session.close()

    @router.put("/{item_id}", response_model=PlaceRead)
    @inject
    async def put(
        self,
        item_id: int,
        item_data: PlacePut,
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> PlaceRead:
        try:
            validated = PlacePut(**item_data.model_dump(exclude_unset=False))
            stmt = (
                update(self.model)
                .where(self.model.id == item_id)
                .values(**validated.model_dump(exclude_unset=False))
                .execution_options(synchronize_session="fetch")
            )
            await session.execute(stmt)
            await session.commit()

            result = await session.execute(
                select(self.model)
                .where(self.model.id == item_id)
                .options(selectinload(Place.photos))
            )
            db_obj = result.scalar_one_or_none()

            if not db_obj:
                raise APIException(code=404, message="Item not found")

            return db_obj
        finally:
            await session.close()

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

    @router.delete("/{place_id}/photos/{photo_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
    @inject
    async def remove_photo(
        self,
        place_id: int,
        photo_id: int,
        use_case: DeletePhotoUseCase = Depends(Provide[Container.delete_photo_use_case]),
    ):
        return await use_case.execute(photo_id, place_id)

    @router.post("/{place_id}/photos/add", status_code=status.HTTP_200_OK)
    @inject
    async def add_photos(
        self,
        request: Request,
        place_id: int,
        photos: Optional[List[UploadFile]] = File(None),
        use_case: PlacePhotosAddUseCase = Depends(Provide[Container.place_photos_add_use_case]),
    ):
        photos_data = (
            [
                ModelPhotoDTO(
                    photo=BytesIO(await photo.read()) if photo else None,
                    filename=photo.filename if photo else None,
                )
                for photo in photos
            ]
            if photos
            else []
        )
        user_id: int = request.state.user.id
        return await use_case.execute(place_id=place_id, user_id=user_id, photos=photos_data)

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

    @router.get(
        "/select_field_values/{field_name}",
        description="Получить допустимые значения для поле по 'field_name'",
    )
    @inject
    async def select_field_values(
        self,
        field_name: str,
        use_case: SelectFieldValuesUseCase = Depends(Provide[Container.select_field_values_use_case]),
    ) -> list[str]:
        return await use_case.execute(
            ModelType.PLACES,
            field_name,
        )
