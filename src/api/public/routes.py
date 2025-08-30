from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, status

from api.admin.schemas import RouteRead
from api.handlers.routes import router as additional_router
from api.permissions.is_authenticated import is_authenticated
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from application.use_cases.routes.copy import RouteCopyUseCase
from application.use_cases.routes.dto import RouteFeedFiltersDTO
from application.use_cases.routes.enums import RouteGenerationMode as Mode
from application.use_cases.routes.feed.list import RouteFeedListUseCase
from application.use_cases.routes.feed.retrieve import RouteFeedRetrieveUseCase
from application.use_cases.tasks.route_generate import StartChatGPTRouteGenerateTaskUseCase
from config.containers import Container
from domain.entities.enums import ModelType
from domain.entities.user import User
from domain.validators.dto import PaginatedResponse

router = APIRouter(
    prefix="/routes",
    tags=["Public Routes"],
    # dependencies=[is_user]
)

router.include_router(additional_router)
# router.include_router(feed_router)


@router.get("/my", response_model=PaginatedResponse[RouteRead], status_code=status.HTTP_200_OK)
# @is_authenticated
@inject
async def list_my_routes(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: ModelObjectListUseCase = Depends(Provide[Container.object_list_use_case]),
) -> PaginatedResponse[RouteRead]:
    """Получить список моих маршрутов"""
    user: User = request.state.user
    return await use_case.execute(
        request=request,
        model_type=ModelType.ROUTES,
        page=page,
        page_size=page_size,
        ObjectDTO=RouteRead,
        filters={"author_id": user.id},
    )


@router.delete("/my/{route_id}/delete", status_code=status.HTTP_204_NO_CONTENT)
# @is_authenticated
@inject
async def delete_my_route(
    request: Request,
    route_id: int,
    use_case: ModelObjectDeleteUseCase = Depends(Provide[Container.object_delete_use_case]),
) -> None:
    """Получить список моих маршрутов"""
    user: User = request.state.user
    await use_case.execute(
        obj_id=route_id,
        model_type=ModelType.ROUTES,
        author_id=user.id,
    )


@router.get("/my/{route_id}", response_model=RouteRead, status_code=status.HTTP_200_OK)
# @is_authenticated
@inject
async def retrieve_my_route(
    request: Request,
    route_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> RouteRead:
    """Получить мой маршрут по ID"""
    user: User = request.state.user
    return await use_case.execute(
        obj_id=route_id, model_type=ModelType.ROUTES, ObjectDTO=RouteRead, filters={"author_id": user.id}
    )


@router.get("/feed", response_model=PaginatedResponse[RouteRead], status_code=status.HTTP_200_OK)
@inject
async def routes_feed(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    filters: RouteFeedFiltersDTO = Depends(),
    use_case: RouteFeedListUseCase = Depends(Provide[Container.route_feed_use_case]),
) -> PaginatedResponse[RouteRead]:
    """Получить ленту маршрутов"""
    routes: PaginatedResponse[RouteRead] = await use_case.execute(
        request=request,
        filters=filters,
        PaginatorModel=RouteRead,
        page=page,
        page_size=page_size,
    )

    return routes


@router.get("/feed/{route_id}", response_model=RouteRead, status_code=status.HTTP_200_OK)
@inject
async def routes_feed(
    route_id: int,
    use_case: RouteFeedRetrieveUseCase = Depends(Provide[Container.route_feed_retrieve_use_case]),
) -> RouteRead:
    """Получить маршрут из ленты"""
    return await use_case.execute(route_id, PaginatorModel=RouteRead)


@router.post("/generate/{survey_id}", status_code=status.HTTP_200_OK)
# @is_authenticated
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


@router.post("/copy/{route_id}", status_code=status.HTTP_201_CREATED)
# @is_authenticated
@inject
async def copy_route(
    request: Request,
    route_id: int,
    use_case: RouteCopyUseCase = Depends(Provide[Container.copy_route_use_case]),
) -> RouteRead:
    user_id: int = request.state.user.id
    return await use_case.execute(route_id, user_id)
