from typing import Type, TypeVar

from pydantic import BaseModel

from sqlalchemy import and_, delete, exists, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.resource import Resource
from infrastructure.models.alchemy.base import Base
from infrastructure.repositories.interfaces.base import Repository, ResourceRepository

TResource = TypeVar("TResource", bound=Resource)


class SqlAlchemyRepository(Repository):
    MODEL: Type[Base]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session


class SqlAlchemyResourceRepository(SqlAlchemyRepository, ResourceRepository[TResource]):
    ENTITY: Type[Resource]
    LIST_DTO: Type[BaseModel]

    ###############
    ### Getters ###
    ###############

    async def get_by_id(self, resource_id: int) -> TResource:
        model = await self._session.get(self.model, resource_id)
        if not model:
            raise ValueError("Resource not found")
        return self.convert_to_entity(model)

    async def get_list(
        self,
        scenario_id: int,
        per_page: int | None = None,
        page: int | None = None,
        ordering: str | None = None,
        filters: dict | None = None,
        show_errors: bool | None = None,
    ) -> list:
        stmt = select(self.MODEL).filter_by(scenario_id=scenario_id)

        if page and per_page:
            stmt = stmt.limit(per_page).offset((page - 1) * per_page)

        stmt = self.apply_ordering(self.MODEL, ordering, stmt)
        stmt = self.apply_filters(self.MODEL, filters, stmt)

        if show_errors:
            result = await self.get_show_error_result(scenario_id, per_page, page)
        else:
            result = await self._session.scalars(
                stmt.order_by(getattr(self.MODEL, "id").desc())
            )

        objects = result.all()
        return [self.LIST_DTO(**vars(obj)) for obj in objects]

    async def filter_by_id_list(self, id_list: list[int]) -> list[TResource]:
        stmt = select(self.MODEL).filter(getattr(self.MODEL, "id").in_(id_list))
        result = await self._session.scalars(stmt)
        return [self.convert_to_entity(row) for row in result.all()]

    ################
    ### Creators ###
    ################

    async def create(self, data: TResource) -> TResource:
        model = self.convert_to_model(data)
        self._session.add(model)
        await self._session.flush()
        return self.convert_to_entity(model)

    async def bulk_create(self, data: list[TResource]) -> list:
        models = [self.convert_to_model(entity) for entity in data]
        self._session.add_all(models)
        await self._session.flush(models)
        return [self.convert_to_entity(model) for model in models]

    ################
    ### Updators ###
    ################

    async def update(self, resource_id: int, data: TResource) -> TResource:
        model = await self._session.get(self.model, resource_id)
        if not model:
            raise ValueError("Resource not found")
        for key, value in data.dict().items():
            setattr(model, key, value)
        await self._session.flush()
        return self.convert_to_entity(model)

    async def bulk_update(self, data: list, batch_size: int = 100000) -> list:
        for i in range(0, len(data), batch_size):
            batch = data[i : i + batch_size]
            await self._session.execute(update(self.MODEL), batch)

        return data

    async def reset_fields(self, scenario_id: int, fields: list[str]) -> None:
        stmt = (
            update(self.MODEL)
            .filter_by(scenario_id=scenario_id)
            .values(**{field: None for field in fields})
        )
        await self._session.execute(stmt)

    ################
    ### Deleters ###
    ################
    async def delete_by_id(self, resource_id: int) -> None:
        model = await self._session.get(self.model, resource_id)
        if not model:
            raise ValueError("Resource not found")
        await self._session.delete(model)
        await self._session.flush()

    async def delete_all(self, scenario_id: int) -> None:
        await self._session.execute(
            delete(self.MODEL).filter(getattr(self.MODEL, "scenario_id") == scenario_id)
        )

    async def delete(self, id_list: list[int]) -> list[int]:
        delete_query = delete(self.MODEL).where(self.MODEL.id.in_(id_list))
        await self._session.execute(delete_query)
        return id_list

    async def exists(self, **filters) -> bool:
        """Проверяет, существует ли объект с заданными параметрами"""
        conditions = [getattr(self.MODEL, field) == value for field, value in filters.items()]
        stmt = select(exists().where(and_(*conditions)))

        result = await self._session.execute(stmt)
        return result.scalar()

    async def check_is_exists_by_name(self, name: str) -> bool:
        pass
