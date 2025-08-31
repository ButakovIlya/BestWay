from io import BytesIO
from typing import List, Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Body, Depends, File, Form, Request, UploadFile, status
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
from application.use_cases.routes.places.add import RoutePlaceAddUseCase
from application.use_cases.routes.places.dto import RoutePlacesOrderUpdateDTO
from application.use_cases.routes.places.remove import RoutePlaceRemoveUseCase
from application.use_cases.routes.places.update_order import RoutePlaceUpdateOrderUseCase
from application.use_cases.tasks.route_generate import StartChatGPTRouteGenerateTaskUseCase
from common.exceptions import APIException
from config.containers import Container
from domain.entities.enums import CityCategory, RouteType
from infrastructure.models.alchemy.routes import Route

router = APIRouter()


@router.post("/", status_code=status.HTTP_200_OK)
@inject
async def create(
    request: Request,
    name: str = Form(...),
    city: Optional[CityCategory] = Form(None),
    type: Optional[RouteType] = Form(None),
    use_case: RouteCreateUseCase = Depends(Provide[Container.route_create_use_case]),
) -> RouteRead:
    user_id: int = request.state.user.id

    data = RouteCreateDTO.from_form(
        name=name,
        author_id=user_id,
        city=city,
        type=type,
    )

    return await use_case.execute(data=data)


@router.post("/{route_id}/places/add/{place_id}", status_code=status.HTTP_200_OK)
@inject
async def add_route_place(
    request: Request,
    route_id: int,
    place_id: int,
    use_case: RoutePlaceAddUseCase = Depends(Provide[Container.route_place_add_use_case]),
) -> None:
    # user_id: int = request.state.user.id

    return await use_case.execute(route_id, place_id)


@router.delete("/{route_id}/places/remove", status_code=status.HTTP_200_OK)
@inject
async def remove_route_place(
    request: Request,
    route_id: int,
    route_place_id: int | None = None,
    use_case: RoutePlaceRemoveUseCase = Depends(Provide[Container.route_place_remove_use_case]),
) -> None:
    """Удалить место по id или удалить все, если ничего не передано"""
    # user_id: int = request.state.user.id

    return await use_case.execute(route_id, route_place_id)


@router.post("/{route_id}/places/update_order", status_code=status.HTTP_200_OK)
@inject
async def update_route_places_order(
    request: Request,
    route_id: int,
    order_info: RoutePlacesOrderUpdateDTO = Body(
        ..., example={"place_id": 1, "place_id": 3, "place_id": 2}
    ),
    use_case: RoutePlaceUpdateOrderUseCase = Depends(Provide[Container.route_place_update_order_use_case]),
) -> None:
    # user_id: int = request.state.user.id

    return await use_case.execute(route_id, order_info)


@router.patch("/{item_id}", response_model=MiniRouteSchema)
@inject
async def patch(
    item_id: int,
    item_data: RoutePatchSchema,
    session: AsyncSession = Depends(Provide[Container.db.session]),
) -> MiniRouteSchema:
    try:
        values = item_data.model_dump(exclude_unset=True)
        if not values:
            raise APIException(code=400, message="Нет данных для обновления")

        stmt = (
            update(Route)
            .where(Route.id == item_id)
            .values(**values)
            .execution_options(synchronize_session="fetch")
        )
        await session.execute(stmt)
        await session.commit()

        result = await session.execute(select(Route).where(Route.id == item_id))
        db_obj = result.scalar_one_or_none()

        if not db_obj:
            raise APIException(code=404, message="Маршрут не найден")

        return db_obj
    finally:
        await session.close()


@router.post("/{route_id}/avatar", status_code=status.HTTP_200_OK)
@inject
async def update_avatar(
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
    route_id: int,
    photo_id: int,
    use_case: DeletePhotoUseCase = Depends(Provide[Container.delete_photo_use_case]),
):
    return await use_case.execute(photo_id, route_id)


@router.post("/{route_id}/photos/add", status_code=status.HTTP_200_OK)
@inject
async def add_photos(
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


@router.post("/generate/{survey_id}", status_code=status.HTTP_200_OK)
@inject
async def generate_route(
    request: Request,
    survey_id: int,
    mode: Mode = Mode.FULL,
    use_case: StartChatGPTRouteGenerateTaskUseCase = Depends(
        Provide[Container.start_route_chatgpt_generate_task]
    ),
) -> str:
    user_id: int = request.state.user.id

    await use_case.execute(user_id, survey_id, mode)
    return "Генерация маршрута запущена"
