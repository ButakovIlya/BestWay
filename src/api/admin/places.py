from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import Select
from sqlalchemy.orm import selectinload

from api.handlers.places import router as additional_router
from api.permissions.is_admin import is_admin
from infrastructure.models.alchemy.routes import Place
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.enums import RoleEnum

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
    router.include_router(additional_router)

    def build_select_stmt(self, item_id: Optional[int] = None, filters: Optional[dict] = None) -> Select:
        stmt = (
            super().build_select_stmt(item_id=item_id, filters=filters).options(selectinload(Place.photos))
        )
        return stmt
