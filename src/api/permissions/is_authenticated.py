from functools import wraps
from typing import Any, Callable

from fastapi import Request

from api.permissions.exceptions import UserIsNotAuthenticatedError


def is_authenticated(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        request = kwargs.get("request")
        if request and request.state.user:
            return await func(*args, **kwargs)
        raise UserIsNotAuthenticatedError()

    return wrapper


async def is_user(request: Request):
    user = getattr(request.state, "user", None)
    if not user:
        raise UserIsNotAuthenticatedError
