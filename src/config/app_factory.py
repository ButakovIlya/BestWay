from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, AsyncGenerator, Callable

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles

import api
from api import admin_routers, public_routers
from api.middlewares.get_jwt_token_user import JwtTokenUserMiddleware
from config.celery import app as celery_app  # noqa
from config.containers import Container
from config.loggers import config_loggers
from config.settings import Settings
from config.uptrace import config_uptrace

from .exceptions import handlers


def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title=settings.app.title,
        debug=settings.app.debug,
        # debug=True,
        version=settings.app.version,
        lifespan=lifespan,
        docs_url=settings.api.docs_url,
        openapi_url=settings.api.openapi_url,
    )
    config_loggers()
    config_uptrace(app)
    add_middlewares(app, settings)

    include_routers(app, settings)
    add_exception_hanlers(app)

    # MEDIA_DIR = Path("storage/media")

    # app.mount(
    #     "/media",
    #     StaticFiles(directory=MEDIA_DIR, check_dir=False),
    #     name="media",
    # )

    app.openapi = custom_openapi(app, settings)  # type: ignore

    return app


def add_exception_hanlers(app: FastAPI) -> None:
    for exception, handler in handlers.items():
        app.add_exception_handler(exception, handler)


def include_routers(app: FastAPI, settings: Settings) -> None:
    for router in admin_routers:
        app.include_router(router, prefix=settings.api.admin_prefix)

    for router in public_routers:
        app.include_router(router, prefix=settings.api.public_prefix)


def add_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(JwtTokenUserMiddleware, settings=settings)
    # app.add_middleware(
    #     DebugToolbarMiddleware,
    #     panels=["debug_toolbar.panels.sqlalchemy.SQLAlchemyPanel"],
    # )


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    async with Container.lifespan(wireable_packages=[api]) as container:
        app.container = container  # type: ignore
        yield


def custom_openapi(app: FastAPI, settings: Settings) -> Callable:
    def wrapper() -> Any:
        if app.openapi_schema:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            routes=app.routes,
        )
        openapi_schema["security"] = [{"BearerAuth": []}]
        openapi_schema["components"]["securitySchemes"] = {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            },
        }

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return wrapper
