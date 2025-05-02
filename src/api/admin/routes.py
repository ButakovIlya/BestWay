from io import BytesIO
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from api.permissions.is_admin import is_admin
from application.use_cases.common.dto import ModelPhotoDTO
from application.use_cases.common.photo.delete import DeletePhotoUseCase
from application.use_cases.routes.add_photos import RoutePhotosAddUseCase
from application.use_cases.routes.avatar import RoutePhotoUpdateUseCase
from application.use_cases.routes.chatgpt_create import ChatGPTRouteCreateUseCase
from application.use_cases.routes.create import RouteCreateUseCase
from application.use_cases.routes.dto import RouteCreateDTO
from config.containers import Container
from domain.entities.enums import CityCategory, RouteType
from infrastructure.models.alchemy.routes import Place, Route, RoutePlace
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.enums import RoleEnum

from .schemas import RouteCreateSchema, RouteFilter, RoutePatchSchema, RoutePutSchema, RouteRead


class RouteViewSet(
    BaseViewSet[RouteCreateSchema, RoutePutSchema, RoutePatchSchema, RouteRead, RouteFilter]
):
    model = Route
    schema_read = RouteRead
    schema_create = RouteCreateSchema
    schema_put = RoutePutSchema
    schema_patch = RoutePatchSchema
    prefix = "/routes"
    tags = ["Routes"]
    authentication_classes = [RoleEnum.ADMIN]

    allowed_methods: list[str] = ["list", "get", "put", "patch", "delete", "options"]

    filter_schema = RouteFilter

    router = APIRouter(tags=tags, prefix=prefix, dependencies=[Depends(is_admin)])

    def build_select_stmt(self, item_id: Optional[int] = None, filters: Optional[dict] = None) -> Select:
        stmt = (
            super()
            .build_select_stmt(item_id=item_id, filters=filters)
            .options(
                joinedload(Route.author),
                joinedload(Route.photos),
                joinedload(Route.places).joinedload(RoutePlace.place).joinedload(Place.photos),
            )
        )
        return stmt

    @router.post("/", status_code=status.HTTP_200_OK)
    @inject
    async def create(
        self,
        request: Request,
        name: str = Form(...),
        city: Optional[CityCategory] = Form(None),
        type: Optional[RouteType] = Form(None),
        duration: Optional[str] = Form(None),
        distance: Optional[str] = Form(None),
        json: Optional[str] = Form(None),
        places: Optional[str] = Form(None),
        photo: Optional[UploadFile] = File(None),
        photos: Optional[List[UploadFile]] = File(None),
        use_case: RouteCreateUseCase = Depends(Provide[Container.route_create_use_case]),
    ) -> RouteRead:
        user_id: int = request.state.user.id

        data = RouteCreateDTO.from_form(
            name=name,
            author_id=user_id,
            city=city,
            type=type,
            duration=duration,
            distance=distance,
            json=json,
            places=places,
        )

        return await use_case.execute(data=data)

    @router.post("/create_route_task_launch", status_code=status.HTTP_200_OK)
    @inject
    async def create_route(
        self,
        use_case: ChatGPTRouteCreateUseCase = Depends(Provide[Container.route_chatgpt_create_use_case]),
    ) -> str:
        await use_case.execute()
        return "Задача запущена"

    @router.post("/{route_id}/avatar", status_code=status.HTTP_200_OK)
    @inject
    async def update_avatar(
        self,
        route_id: int,
        photo: Optional[UploadFile] = File(None),
        use_case: RoutePhotoUpdateUseCase = Depends(Provide[Container.route_avatar_update_use_case]),
    ):
        data = ModelPhotoDTO(
            photo=BytesIO(await photo.read()) if photo else None,
            filename=photo.filename if photo else None,
        )
        return await use_case.execute(route_id=route_id, data=data)

    @router.delete("/{route_id}/photos/{photo_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
    @inject
    async def remove_photo(
        self,
        route_id: int,
        photo_id: int,
        use_case: DeletePhotoUseCase = Depends(Provide[Container.delete_photo_use_case]),
    ):
        return await use_case.execute(photo_id, route_id)

    @router.post("/{route_id}/photos/add", status_code=status.HTTP_200_OK)
    @inject
    async def add_photos(
        self,
        request: Request,
        route_id: int,
        photos: Optional[List[UploadFile]] = File(None),
        use_case: RoutePhotosAddUseCase = Depends(Provide[Container.route_photos_add_use_case]),
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
        return await use_case.execute(route_id=route_id, user_id=user_id, photos=photos_data)
