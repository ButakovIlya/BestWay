from fastapi import Request

from api.permissions.exceptions import UserIsNotAdminError


async def is_admin(request: Request):
    user = getattr(request.state, "user", None)
    if not user or not getattr(user, "is_admin", False):
        raise UserIsNotAdminError
