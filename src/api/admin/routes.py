from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from api.handlers.routes import router as additional_router
from api.permissions.is_admin import is_admin
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
    router.include_router(additional_router)

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
