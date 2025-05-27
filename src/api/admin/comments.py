from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from api.permissions.is_admin import is_admin
from infrastructure.models.alchemy.routes import Comment
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.enums import RoleEnum

from .schemas import CommentCreate, CommentFilter, CommentPatch, CommentPut, CommentRead


class CommentViewSet(BaseViewSet[CommentCreate, CommentPut, CommentPatch, CommentRead, CommentFilter]):
    model = Comment
    schema_read = CommentRead
    schema_create = CommentCreate
    schema_put = CommentPut
    schema_patch = CommentPatch

    filter_schema = CommentFilter
    ilike_list = ["comment"]

    prefix = "/comments"
    tags = ["Comments"]

    allowed_methods: list[str] = ["list", "get", "put", "patch", "delete", "options"]

    authentication_classes = [RoleEnum.ADMIN]

    router = APIRouter(tags=tags, prefix=prefix, dependencies=[Depends(is_admin)])

    def build_select_stmt(self, item_id: Optional[int] = None, filters: Optional[dict] = None) -> Select:
        stmt = (
            super().build_select_stmt(item_id=item_id, filters=filters).options(joinedload(Comment.author))
        )
        return stmt
