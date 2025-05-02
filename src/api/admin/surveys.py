from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from api.permissions.is_admin import is_admin
from infrastructure.models.alchemy.surveys import Survey
from infrastructure.orm.base import BaseViewSet
from infrastructure.permissions.enums import RoleEnum

from .schemas import SurveyCreate, SurveyFilter, SurveyPatch, SurveyPut, SurveyRead


class SurveyViewSet(BaseViewSet[SurveyCreate, SurveyPut, SurveyPatch, SurveyRead, SurveyFilter]):
    model = Survey
    schema_read = SurveyRead
    schema_create = SurveyCreate
    schema_put = SurveyPut
    schema_patch = SurveyPatch

    filter_schema = SurveyFilter
    ilike_list = ["name"]

    prefix = "/surveys"
    tags = ["Surveys"]

    allowed_methods: list[str] = ["list", "get", "create", "put", "patch", "delete", "options"]

    authentication_classes = [RoleEnum.ADMIN]

    router = APIRouter(tags=tags, prefix=prefix, dependencies=[Depends(is_admin)])

    def build_select_stmt(self, item_id: Optional[int] = None, filters: Optional[dict] = None) -> Select:
        stmt = super().build_select_stmt(item_id=item_id, filters=filters)
        stmt = stmt.options(joinedload(Survey.author))
        return stmt
