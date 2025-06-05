from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, Response, status

from api.handlers.places import router as additional_router
from api.permissions.is_admin import is_admin
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from config.containers import Container
from domain.entities.enums import ModelType
from domain.validators.dto import PaginatedResponse

from .schemas import PlaceRead

# router = APIRouter(tags=["Places"], prefix="/places", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Places"], prefix="/places")
router.include_router(additional_router)


@router.get("/", response_model=PaginatedResponse[PlaceRead], status_code=status.HTTP_200_OK)
@inject
async def list_places(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: ModelObjectListUseCase = Depends(Provide[Container.object_list_use_case]),
) -> PaginatedResponse[PlaceRead]:
    """Получить список мест"""
    return await use_case.execute(
        request=request,
        model_type=ModelType.PLACES,
        page=page,
        page_size=page_size,
        ObjectDTO=PlaceRead,
    )


@router.get("/{place_id}", response_model=PlaceRead, status_code=status.HTTP_200_OK)
@inject
async def retrieve_place(
    place_id: int,
    use_case: ModelObjectRetrieveUseCase = Depends(Provide[Container.object_retrieve_use_case]),
) -> PlaceRead:
    """Получить место по ID"""
    return await use_case.execute(
        obj_id=place_id,
        model_type=ModelType.PLACES,
        ObjectDTO=PlaceRead,
    )


@router.delete("/{place_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_place(
    place_id: int,
    use_case: ModelObjectDeleteUseCase = Depends(Provide[Container.object_delete_use_case]),
) -> Response:
    """Удалить место"""
    await use_case.execute(
        obj_id=place_id,
        model_type=ModelType.PLACES,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
