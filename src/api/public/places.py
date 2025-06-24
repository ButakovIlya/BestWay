from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, status

from api.admin.schemas import PlaceRead
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from application.use_cases.places.feed import PlaceFeedListUseCase
from common.dto import PlacesFiltersDTO
from config.containers import Container
from domain.entities.enums import ModelType
from domain.validators.dto import PaginatedResponse

# router = APIRouter(tags=["Places"], prefix="/places", dependencies=[Depends(is_user)])
router = APIRouter(tags=["Public Places"], prefix="/places")


@router.get("/", response_model=PaginatedResponse[PlaceRead], status_code=status.HTTP_200_OK)
@inject
async def list_places(
    request: Request,
    filters: PlacesFiltersDTO = Depends(),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: PlaceFeedListUseCase = Depends(Provide[Container.place_feed_use_case]),
) -> PaginatedResponse[PlaceRead]:
    """Получить список мест"""
    return await use_case.execute(
        filters=filters,
        request=request,
        page=page,
        page_size=page_size,
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
