from typing import List, Protocol

from fastapi import Depends, HTTPException, Request

from infrastructure.permissions.constants import ROLE_PERMISSION_MAP
from infrastructure.permissions.enums import PermissionEnum, RoleEnum


# --- Протокол для кастомных проверок (если нужно) ---
class BasePermission(Protocol):
    async def __call__(self, request: Request) -> bool: ...


# --- Depends для проверки роли ---
def role_dependency(allowed_roles: List[RoleEnum]):
    async def wrapper(request: Request):
        user = getattr(request.state, "user", None)
        if not user or not hasattr(user, "role"):
            raise HTTPException(status_code=401, detail="Unauthorized")
        if user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Role not allowed")

    return Depends(wrapper)


# --- Depends для проверки прав ---
def permission_dependency(required_permissions: List[PermissionEnum]):
    async def wrapper(request: Request):
        user = getattr(request.state, "user", None)
        if not user or not hasattr(user, "role"):
            raise HTTPException(status_code=401, detail="Unauthorized")

        role: RoleEnum = user.role
        allowed_permissions = ROLE_PERMISSION_MAP.get(role, [])

        if not any(perm in allowed_permissions for perm in required_permissions):
            raise HTTPException(status_code=403, detail="Permission denied")

    return Depends(wrapper)
