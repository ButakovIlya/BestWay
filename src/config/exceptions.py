from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class APIException(Exception):
    def __init__(self, code: int, message: str, link: str = ""):
        self.code = code
        self.message = message
        self.link = link


async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.code,
        content={
            "code": exc.code,
            "message": exc.message,
            "link": exc.link
        }
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
            "link": "https://docs.api/errors#validation"
        }
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
            "link": "https://docs.api/errors#validation"
        }
    )

handlers = {
    APIException: api_exception_handler,
    # RequestValidationError: request_validation_exception_handler,
    # ValidationError: pydantic_validation_exception_handler,

}
