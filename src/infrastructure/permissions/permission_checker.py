from functools import wraps
from typing import Any, Callable
from infrastructure.permissions.exceptions import UserHasNoPermissionError


def check_permissions(required_permissions: list[str]) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            request = kwargs.get("request")
            if request and not set(request.state.user.permissions).issuperset(
                set(required_permissions)
            ):
                raise UserHasNoPermissionError()
            return await func(*args, **kwargs)

        return wrapper

    return decorator

