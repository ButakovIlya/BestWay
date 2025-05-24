from fastapi import APIRouter

from api.admin.places import PlaceViewSet
from infrastructure.permissions.enums import RoleEnum


class PublicPlaceViewSet(PlaceViewSet):
    prefix = "/places"
    tags = ["Places"]

    allowed_methods: list[str] = ["list", "get", "options"]

    authentication_classes = [RoleEnum.USER]

    router = APIRouter(tags=tags, prefix=prefix)
