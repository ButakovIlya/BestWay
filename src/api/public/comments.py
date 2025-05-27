from api.admin.comments import CommentViewSet
from infrastructure.permissions.enums import RoleEnum


class PublicCommentViewSet(CommentViewSet):
    allowed_methods: list[str] = ["list", "get", "create", "put", "patch", "delete", "options"]

    authentication_classes = [RoleEnum.USER]
