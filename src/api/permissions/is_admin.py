from functools import wraps
from typing import Any, Callable

from api.permissions.exceptions import UserIsNotAdminError


def is_admin(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        request = kwargs.get("request")
        if request and request.state.user and request.state.user.is_admin:
            return await func(*args, **kwargs)
        raise UserIsNotAdminError()

    return wrapper
