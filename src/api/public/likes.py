from api.admin.likes import LikeViewSet
from infrastructure.permissions.enums import RoleEnum


class PublicLikeViewSet(LikeViewSet):

    allowed_methods: list[str] = ["list", "get", "create", "put", "patch", "delete", "options"]

    authentication_classes = [RoleEnum.USER]
