from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import api
from api import routers
from api.middlewares.get_jwt_token_user import JwtTokenUserMiddleware
from config.celery import app as celery_app  # noqa
from config.containers import Container
from config.loggers import config_loggers
from config.settings import Settings
from config.uptrace import config_uptrace

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

from .exceptions import handlers

def create_app(settings: Settings) -> FastAPI:
    app = FastAPI(
        title=settings.app.title,
        debug=settings.app.debug,
        version=settings.app.version,
        lifespan=lifespan,
        docs_url=settings.api.docs_url,
        openapi_url=settings.api.openapi_url,
    )
    config_loggers()
    config_uptrace(app)
    add_middlewares(app, settings)
    include_routers(app, settings)
    # add_exception_hanlers(app)
    return app



def add_exception_hanlers(app: FastAPI) -> None:
    for exception, handler in handlers.items():
        app.add_exception_handler(exception, handler)

def include_routers(app: FastAPI, settings: Settings) -> None:
    for router in routers:
        app.include_router(router, prefix=settings.api.prefix)


def add_middlewares(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(JwtTokenUserMiddleware, settings=settings)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    async with Container.lifespan(wireable_packages=[api]) as container:
        app.container = container  # type: ignore
        yield
