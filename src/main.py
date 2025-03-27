from fastapi import Request
from fastapi.responses import JSONResponse

from config.app_factory import create_app
from config.exceptions import APIException
from config.settings import Settings

app = create_app(Settings())


@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.code,
        content={"code": exc.code, "message": exc.message, "link": exc.link},
    )


# @app.exception_handler(ValueError)
# async def value_error_exception_handler(request: Request, exc: ValueError):
#     return JSONResponse(
#         status_code=400,
#         content={"detail": str(exc)},
#     )

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     print(exc.errors())
#     return JSONResponse(
#         status_code=422,
#         content={"error": "Validation failed", "details": exc.errors()}
#     )
