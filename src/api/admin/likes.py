from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from api.permissions.is_admin import is_admin
from infrastructure.models.alchemy.routes import Like
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.enums import RoleEnum

from .schemas import LikeCreate, LikeFilter, LikePatch, LikePut, LikeRead


class LikeViewSet(BaseViewSet[LikeCreate, LikePut, LikePatch, LikeRead, LikeFilter]):
    model = Like
    schema_read = LikeCreate
    schema_create = LikeCreate
    schema_put = LikePut
    schema_patch = LikePatch

    filter_schema = LikeFilter

    prefix = "/likes"
    tags = ["Likes"]

    allowed_methods: list[str] = ["list", "get", "put", "patch", "delete", "options"]

    authentication_classes = [RoleEnum.ADMIN]

    router = APIRouter(tags=tags, prefix=prefix, dependencies=[Depends(is_admin)])

    def build_select_stmt(self, item_id: Optional[int] = None, filters: Optional[dict] = None) -> Select:
        stmt = super().build_select_stmt(item_id=item_id, filters=filters).options(joinedload(Like.author))
        return stmt
