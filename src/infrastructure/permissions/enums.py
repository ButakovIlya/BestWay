from enum import Enum


class RoleEnum(str, Enum):
    """Роли"""

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    USER = "user"

    def level(self) -> int:
        hierarchy = {
            RoleEnum.USER: 0,
            RoleEnum.ADMIN: 1,
            RoleEnum.SUPER_ADMIN: 2,
        }
        return hierarchy[self]


class PermissionEnum(str, Enum):
    """Права доступа"""

    # Базовые
    ALLOW_ANY = "allow_any"
    AUTHENTICATED_ONLY = "authenticated_only"

    # CRUD
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    PATCH = "patch"
    DELETE = "delete"
