from typing import List

from infrastructure.permissions.enums import PermissionEnum, RoleEnum

# --- Привязка прав к ролям (жёстко заданная логика) ---
ROLE_PERMISSION_MAP: dict[RoleEnum, List[PermissionEnum]] = {
    RoleEnum.ADMIN: [
        PermissionEnum.CREATE,
        PermissionEnum.DELETE,
        PermissionEnum.VIEW,
        PermissionEnum.UPDATE,
    ],
    RoleEnum.USER: [PermissionEnum.VIEW, PermissionEnum.CREATE],
}
