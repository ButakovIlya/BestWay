from typing import Callable, List

from infrastructure.permissions.dependencies import permission_dependency, role_dependency
from infrastructure.permissions.enums import PermissionEnum, RoleEnum


# --- Отдельные декораторы ---
def has_roles(roles: List[RoleEnum]):
    def decorator(func: Callable):
        if not hasattr(func, "__fastapi_dependencies__"):
            func.__fastapi_dependencies__ = []
        func.__fastapi_dependencies__.append(role_dependency(roles))
        return func

    return decorator


def has_permissions(perms: List[PermissionEnum]):
    def decorator(func: Callable):
        if not hasattr(func, "__fastapi_dependencies__"):
            func.__fastapi_dependencies__ = []
        func.__fastapi_dependencies__.append(permission_dependency(perms))
        return func

    return decorator


# --- Универсальный декоратор для обоих сразу ---
def access_control(roles: List[RoleEnum] = None, permissions: List[PermissionEnum] = None):
    def decorator(func: Callable):
        if not hasattr(func, "__fastapi_dependencies__"):
            func.__fastapi_dependencies__ = []
        if roles:
            func.__fastapi_dependencies__.append(role_dependency(roles))
        if permissions:
            func.__fastapi_dependencies__.append(permission_dependency(permissions))
        return func

    return decorator
