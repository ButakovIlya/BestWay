from functools import wraps
from typing import Any, Callable

from api.permissions.exceptions import UserIsNotAuthenticatedError


def is_authenticated(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        request = kwargs.get("request")
        if request and request.state.user:
            return await func(*args, **kwargs)
        raise UserIsNotAuthenticatedError()

    return wrapper
