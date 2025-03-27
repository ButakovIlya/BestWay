from enum import Enum


class RoleEnum(str, Enum):
    """Роли"""
    ADMIN = "admin"
    USER = "user"


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