import inspect
from typing import Generic, List, Type, TypeVar

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Response, status
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from config.containers import Container
from config.exceptions import APIException
from infrastructure.models.alchemy.base import Base
from infrastructure.permissions.dependencies import request_body_schema_from_self, role_required
from infrastructure.permissions.enums import PermissionEnum, RoleEnum

TRead = TypeVar("TRead", bound=BaseModel)
TCreate = TypeVar("TCreate", bound=BaseModel)
TPut = TypeVar("TPut", bound=BaseModel)
TPatch = TypeVar("TPatch", bound=BaseModel)


class BaseViewSet(Generic[TRead, TCreate, TPut, TPatch]):
    model: Type[Base]
    schema_read: Type[TRead]
    schema_create: Type[TCreate]
    schema_put: Type[TPut]
    schema_patch: Type[TPut]
    prefix: str
    tags: list

    authentication_classes: list[RoleEnum] = []

    permissions: dict[str, list[PermissionEnum]] = {
        "list": [PermissionEnum.ALLOW_ANY],
        "get": [PermissionEnum.ALLOW_ANY],
        "create": [PermissionEnum.ALLOW_ANY],
        "update": [PermissionEnum.ALLOW_ANY],
        "patch": [PermissionEnum.ALLOW_ANY],
        "delete": [PermissionEnum.ALLOW_ANY],
    }

    allowed_methods: list[str] = ["list", "get", "create", "put", "patch", "delete", "options"]

    def __init__(self):
        self.router = APIRouter(
            prefix=self.prefix,
            tags=self.tags,
            dependencies=[Depends(role_required(self.authentication_classes))],
        )

        # Create
        if "create" in self.allowed_methods:
            self.router.add_api_route(
                "/",
                self.create,
                response_model=self.schema_read,
                methods=["POST"],
                name=f"{self.model.__name__}_create",
                summary=f"Create {self.model.__name__}",
                openapi_extra={
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": self.schema_create.model_json_schema()}},
                    }
                },
            )

        if "list" in self.allowed_methods:
            self.router.add_api_route(
                "/",
                self.list,
                response_model=List[self.schema_read],
                methods=["GET"],
                name=f"{self.model.__name__}_list",
            )

        if "get" in self.allowed_methods:
            self.router.add_api_route(
                "/{item_id}",
                self.get,
                response_model=self.schema_read,
                methods=["GET"],
                name=f"{self.model.__name__}_get",
            )

        if "put" in self.allowed_methods:
            self.router.add_api_route(
                "/{item_id}",
                self.put,
                response_model=self.schema_read,
                methods=["PUT"],
                name=f"{self.model.__name__}_put",
                openapi_extra={
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": self.schema_put.model_json_schema()}},
                    }
                },
            )

        if "patch" in self.allowed_methods:
            self.router.add_api_route(
                "/{item_id}",
                self.patch,
                response_model=self.schema_read,
                methods=["PATCH"],
                name=f"{self.model.__name__}_patch",
                openapi_extra={
                    "requestBody": {
                        "required": True,
                        "content": {"application/json": {"schema": self.schema_patch.model_json_schema()}},
                    }
                },
            )

        if "delete" in self.allowed_methods:
            self.router.add_api_route(
                "/{item_id}",
                self.delete,
                status_code=status.HTTP_204_NO_CONTENT,
                response_class=Response,
                methods=["DELETE"],
                name=f"{self.model.__name__}_delete",
            )

        # добавляем в роутинг методы класса
        custom_router = getattr(self.__class__, "router", None)
        if isinstance(custom_router, APIRouter):
            for route in custom_router.routes:
                if isinstance(route, APIRoute):
                    # Привязываем endpoint к self, если это метод
                    if inspect.isfunction(route.endpoint) and hasattr(route.endpoint, "__get__"):
                        bound_endpoint = route.endpoint.__get__(self)
                        new_route = APIRoute(
                            path=route.path,
                            endpoint=bound_endpoint,
                            methods=route.methods,
                            name=route.name,
                            response_model=route.response_model,
                            status_code=route.status_code,
                            summary=route.summary,
                            description=route.description,
                            response_description=route.response_description,
                            dependencies=route.dependencies,
                            tags=route.tags or self.tags,
                            responses=route.responses,
                            callbacks=route.callbacks,
                            deprecated=route.deprecated,
                            operation_id=route.operation_id,
                            openapi_extra=route.openapi_extra,
                        )
                        self.router.routes.append(new_route)
                    else:
                        self.router.routes.append(route)

    @inject
    async def list(self, session: AsyncSession = Depends(Provide[Container.db.session])) -> List[TRead]:
        try:
            result = await session.execute(select(self.model))
            return result.scalars().all()
        finally:
            await session.close()

    @inject
    async def get(
        self,
        item_id: int,
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> TRead:
        try:
            result = await session.execute(select(self.model).where(self.model.id == item_id))
            obj = result.scalar_one_or_none()
            if not obj:
                raise APIException(code=404, message="Item not found")
            return obj
        finally:
            await session.close()

    @inject
    async def create(
        self,
        item_data: TCreate = Depends(request_body_schema_from_self),
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> TRead:
        try:
            db_obj = self.model(**item_data.model_dump())
            session.add(db_obj)
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        finally:
            await session.close()

    @inject
    async def put(
        self,
        item_id: int,
        item_data: TPut = Depends(request_body_schema_from_self),
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> TRead:
        try:
            validated = self.schema_put(**item_data.model_dump(exclude_unset=False))
            stmt = (
                update(self.model)
                .where(self.model.id == item_id)
                .values(**validated.model_dump(exclude_unset=False))
                .execution_options(synchronize_session="fetch")
            )

            await session.execute(stmt)
            await session.commit()

            result = await session.execute(select(self.model).where(self.model.id == item_id))
            db_obj = result.scalar_one_or_none()

            if not db_obj:
                raise APIException(code=404, message="Item not found")

            return db_obj
        finally:
            await session.close()

    @inject
    async def patch(
        self,
        item_id: int,
        item_data: TPatch = Depends(request_body_schema_from_self),
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> TRead:
        try:
            values = item_data.model_dump(exclude_unset=True)

            if not values:
                raise APIException(code=400, message="Нет данных для обновления")

            stmt = (
                update(self.model)
                .where(self.model.id == item_id)
                .values(**values)
                .execution_options(synchronize_session="fetch")
            )

            await session.execute(stmt)
            await session.commit()

            result = await session.execute(select(self.model).where(self.model.id == item_id))
            db_obj = result.scalar_one_or_none()

            if not db_obj:
                raise APIException(code=404, message="Item not found")

            return db_obj
        finally:
            await session.close()

    @inject
    async def delete(
        self,
        item_id: int,
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> Response:
        try:
            result = await session.execute(select(self.model).where(self.model.id == item_id))
            db_obj = result.scalar_one_or_none()
            if not db_obj:
                raise APIException(code=404, message="Item not found")

            await session.delete(db_obj)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        finally:
            await session.close()
