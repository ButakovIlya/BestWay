import inspect
from collections import defaultdict
from typing import Any, Generic, List, Optional, Type, TypeVar
from urllib.parse import urlencode

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request, Response, status
from fastapi.routing import APIRoute
from pydantic import BaseModel
from sqlalchemy import Select, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from common.exceptions import APIException
from config.containers import Container
from domain.validators.dto import PaginatedResponse
from infrastructure.models.alchemy.base import Base
from infrastructure.permissions.dependencies import (
    request_body_schema_from_self,
    request_patch_schema_from_self,
    request_put_schema_from_self,
    role_required,
)
from infrastructure.permissions.enums import PermissionEnum, RoleEnum

TRead = TypeVar("TRead", bound=BaseModel)
TCreate = TypeVar("TCreate", bound=BaseModel)
TPut = TypeVar("TPut", bound=BaseModel)
TPatch = TypeVar("TPatch", bound=BaseModel)
TFilter = TypeVar("TFilter", bound=BaseModel)


class BaseViewSet(Generic[TRead, TCreate, TPut, TPatch, TFilter]):
    model: Type[Base]
    schema_read: Type[TRead]
    schema_create: Type[TCreate]
    schema_put: Type[TPut]
    schema_patch: Type[TPut]

    filter_schema: Type[TFilter]
    ilike_list: List = []

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

    pagination_class: Optional[Type[PaginatedResponse]] = PaginatedResponse

    def __init__(self):
        self.router = APIRouter(
            prefix=self.prefix,
            tags=self.tags,
            # dependencies=[Depends(role_required(self.authentication_classes))],
        )

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
            if self.pagination_class:
                response_model = self.pagination_class[self.schema_read]
            else:
                response_model = List[self.schema_read]

            self.router.add_api_route(
                "/",
                self.list,
                response_model=response_model,
                methods=["GET"],
                name=f"{self.model.__name__}_list",
                dependencies=[],
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

    async def get_object(
        self,
        item_id: int,
        session: AsyncSession,
    ) -> Base:
        result = await self.get_queryset(session, item_id)
        obj = result.unique().scalar_one_or_none()
        if not obj:
            raise APIException(code=404, message="Item not found")
        return obj

    async def get_queryset(
        self,
        session: AsyncSession,
        item_id: Optional[int] = None,
        filters: Optional[dict] = None,
    ) -> Result:
        stmt = self.build_select_stmt(item_id=item_id, filters=filters)
        return await session.execute(stmt)

    def build_select_stmt(self, item_id: Optional[int] = None, filters: Optional[dict] = None) -> Select:
        stmt = select(self.model)

        if item_id:
            stmt = stmt.where(self.model.id == item_id)

        if filters:
            for attr, value in filters.items():
                if value is None:
                    continue

                if attr.endswith("__list"):
                    column_name = attr.removesuffix("__list")
                    if hasattr(self.model, column_name):
                        stmt = stmt.where(getattr(self.model, column_name).in_(value))
                elif attr in self.ilike_list:
                    stmt = stmt.where(getattr(self.model, attr).ilike(f"%{value}%"))
                elif hasattr(self.model, attr):
                    stmt = stmt.where(getattr(self.model, attr) == value)

        return stmt

    async def paginate_queryset(
        self,
        result: Result,
        request: Request,
        page: int = 1,
        page_size: int = 10,
    ) -> BaseModel:
        items = result.unique().scalars().all()
        total = len(items)

        start = (page - 1) * page_size
        end = start + page_size
        paginated = items[start:end]

        paginated_data = [self.schema_read.model_validate(obj) for obj in paginated]

        base_url = str(request.url).split("?")[0]
        query_params = dict(request.query_params)

        def build_url(page_number: int) -> Optional[str]:
            if page_number < 1 or page_number > (total + page_size - 1) // page_size:
                return None
            params = {**query_params, "page": page_number, "page_size": page_size}
            return f"{base_url}?{urlencode(params)}"

        return self.pagination_class(
            data=paginated_data,
            count=total,
            page=page,
            next=build_url(page + 1),
            previous=build_url(page - 1),
        )

    @inject
    async def list(
        self,
        request: Request,
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> Any:
        try:
            filter_obj = self.parse_query_filters(request)
            filters = filter_obj.model_dump(exclude_none=True)
            result = await self.get_queryset(session, filters=filters)

            # Пагинация включена
            if self.pagination_class:
                page = int(request.query_params.get("page", 1))
                page_size = int(request.query_params.get("page_size", 10))
                return await self.paginate_queryset(result, request, page=page, page_size=page_size)

            # Без пагинации — сериализация в схемы
            items = result.unique().scalars().all()
            return [self.schema_read.model_validate(obj) for obj in items]
        finally:
            await session.close()

    @inject
    async def get(
        self,
        item_id: int,
        session: AsyncSession = Depends(Provide[Container.db.session]),
    ) -> TRead:
        try:
            orm_obj = await self.get_object(item_id, session)

            return self.schema_read.model_validate(orm_obj)

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
        item_data: TPut = Depends(request_put_schema_from_self),
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
        item_data: TPatch = Depends(request_patch_schema_from_self),
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

    def parse_query_filters(self, request: Request) -> TFilter:
        raw_query = defaultdict(list)
        for key, value in request.query_params.multi_items():
            raw_query[key].append(value)
        raw_filters = {k: v[0] if len(v) == 1 else v for k, v in raw_query.items()}
        return self.filter_schema(**raw_filters)
