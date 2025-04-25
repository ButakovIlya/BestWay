from typing import Callable

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from common.exceptions import APIException
from domain.exceptions import DomainException
from src.api.permissions.exceptions import UserIsNotAdminError, UserIsNotAuthenticatedError


def create_exception_handler(
    status_code: int,
) -> Callable[[Request, Exception | DomainException], Response]:

    def get_exception_handler(request: Request, exc: Exception | DomainException) -> Response:
        if isinstance(exc, DomainException):
            return api_exception_handler(request, exc)
        return exception_handler(request, exc)

    def api_exception_handler(request: Request, exc: DomainException) -> Response:
        code = str(exc.code)
        message = exc.message

        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "code": code,
                    "message": message,
                },
            },
        )

    def exception_handler(request: Request, exc: Exception) -> Response:
        return Response(
            status_code=500,
            content={"error": f"An unexpected error occurred: {exc}"},
        )

    return get_exception_handler


async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message},
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError):
    error_messages = "; ".join(
        f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": f"Ошибка валидации: {error_messages}",
            "link": "https://docs.api/errors#validation",
        },
    )


async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    error_messages = "; ".join(
        f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}" for err in exc.errors()
    )
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": f"Ошибка валидации: {error_messages}",
            "link": "https://docs.api/errors#validation",
        },
    )


handlers = {
    APIException: api_exception_handler,
    UserIsNotAdminError: create_exception_handler(status_code=403),
    UserIsNotAuthenticatedError: create_exception_handler(status_code=403),
    # RequestValidationError: request_validation_exception_handler,
    # ValidationError: pydantic_validation_exception_handler,
}
