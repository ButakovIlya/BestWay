from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, Response, status

from api.handlers.routes import router as additional_router
from api.permissions.is_admin import is_admin
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from config.containers import Container
from domain.entities.enums import ModelType
from domain.validators.dto import PaginatedResponse

from .schemas import RouteRead

# router = APIRouter(tags=["Routes"], prefix="/routes", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Routes"], prefix="/routes")
router.include_router(additional_router)


@router.get("/", response_model=PaginatedResponse[RouteRead], status_code=status.HTTP_200_OK)
@inject
async def list_routes(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: ModelObjectListUseCase = Depends(Provide[Container.object_list_use_case]),
) -> PaginatedResponse[RouteRead]:
    """Получить список маршрутов"""
    return await use_case.execute(
        request=request,
        model_type=ModelType.ROUTES,
        page=page,
        page_size=page_size,
        ObjectDTO=RouteRead,
    )


@router.get("/{route_id}", response_model=RouteRead, status_code=status.HTTP_200_OK)
@inject
async def retrieve_route(
    route_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> RouteRead:
    """Получить маршрут по ID"""
    return await use_case.execute(
        obj_id=route_id,
        model_type=ModelType.ROUTES,
        ObjectDTO=RouteRead,
    )


@router.delete("/{route_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_route(
    route_id: int,
    use_case: ModelObjectDeleteUseCase = Depends(Provide[Container.object_delete_use_case]),
) -> Response:
    """Удалить маршрут"""
    await use_case.execute(
        obj_id=route_id,
        model_type=ModelType.ROUTES,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
