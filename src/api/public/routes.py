from fastapi import APIRouter

from api.admin.routes import RouteViewSet
from api.handlers.routes import router as additional_router
from infrastructure.permissions.enums import RoleEnum


class PublicRouteViewSet(RouteViewSet):
    prefix = "/routes"
    tags = ["Routes"]

    authentication_classes = [RoleEnum.ADMIN]

    router = APIRouter(tags=tags, prefix=prefix)
    router.include_router(additional_router)
