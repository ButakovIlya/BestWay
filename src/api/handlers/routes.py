from io import BytesIO
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, File, Form, Request, UploadFile, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from api.admin.schemas import MiniRouteSchema, RoutePatchSchema, RouteRead
from application.use_cases.common.dto import ModelPhotoDTO
from application.use_cases.common.photo.delete import DeletePhotoUseCase
from application.use_cases.routes.add_photos import RoutePhotosAddUseCase
from application.use_cases.routes.avatar import RoutePhotoUpdateUseCase
from application.use_cases.routes.create import RouteCreateUseCase
from application.use_cases.routes.dto import RouteCreateDTO
from application.use_cases.routes.enums import RouteGenerationMode as Mode
from application.use_cases.tasks.route_generate import StartChatGPTRouteGenerateTaskUseCase
from common.exceptions import APIException
from config.containers import Container
from domain.entities.enums import CityCategory, RouteType

router = APIRouter()


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


@router.patch("/{item_id}", response_model=MiniRouteSchema)
@inject
async def patch(
    self,
    item_id: int,
    item_data: RoutePatchSchema,
    session: AsyncSession = Depends(Provide[Container.db.session]),
) -> MiniRouteSchema:
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

        result = await session.execute(select(self.model).where(self.model.id == item_id))
        db_obj = result.scalar_one_or_none()

        if not db_obj:
            raise APIException(code=404, message="Маршрут не найден")

        return db_obj
    finally:
        await session.close()


@router.post("/generate/{survey_id}", status_code=status.HTTP_200_OK)
@inject
async def create_route(
    self,
    request: Request,
    survey_id: int,
    mode: Mode = Mode.FULL,
    use_case: StartChatGPTRouteGenerateTaskUseCase = Depends(
        Provide[Container.start_route_chatgpt_generate_task]
    ),
) -> str:
    user_id: int = request.state.user.id

    await use_case.execute(user_id, survey_id, mode)
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
