from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from infrastructure.models.alchemy.routes import Place, Route, RoutePlace
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.enums import RoleEnum

from .schemas import PlaceFilter, RouteCreateSchema, RoutePatchSchema, RoutePutSchema, RouteSchema


class RouteViewSet(
    BaseViewSet[RouteSchema, RouteCreateSchema, RoutePutSchema, RoutePatchSchema, PlaceFilter]
):
    model = Route
    schema_read = RouteSchema
    schema_create = RouteCreateSchema
    schema_put = RoutePutSchema
    schema_patch = RoutePatchSchema
    prefix = "/routes"
    tags = ["Routes"]
    authentication_classes = [RoleEnum.ADMIN]

    filter_schema = PlaceFilter

    async def get_queryset(self, session: AsyncSession, item_id: Optional[int] = None):
        stmt = select(Route).options(
            joinedload(Route.author),
            joinedload(Route.photos),
            joinedload(Route.places).joinedload(RoutePlace.place).joinedload(Place.photos),
        )
        if item_id:
            stmt = stmt.where(Route.id == item_id)
        return await session.execute(stmt)

    async def paginate_queryset(self, result):
        return result.scalars().all()

    # @inject
    # async def create(
    #     self,
    #     data: RouteCreateSchema = Body(...),
    #     photos: Optional[List[UploadFile]] = List[File(None)],
    #     use_case: PlacePhotoUpdateUseCase = Depends(Provide[Container.place_avatar_update_use_case]),
    # ) -> RouteSchema:
    #     place_ids = data.place_ids
    #     route_data = data.model_dump(exclude={"place_ids"})

    #     use_case.execute()
