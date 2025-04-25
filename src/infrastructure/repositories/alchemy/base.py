from typing import Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import JSON, String, and_, cast, delete, distinct, exists, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.sqltypes import Enum as SAEnum

from common.exceptions import APIException
from domain.entities.model import Model
from infrastructure.models.alchemy.base import Base
from infrastructure.repositories.interfaces.base import ModelRepository, Repository

TModel = TypeVar("TModel", bound=Model)


class SqlAlchemyRepository(Repository):
    MODEL: Type[Base]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session


class SqlAlchemyModelRepository(SqlAlchemyRepository, ModelRepository[TModel]):
    ENTITY: Type[Model]
    LIST_DTO: Type[BaseModel]

    async def get_field_values(
        self,
        name: str,
        per_page: int | None = None,
        page: int | None = None,
    ) -> list:
        field: InstrumentedAttribute = getattr(self.MODEL, name)
        is_json_field = isinstance(field.type, JSON)

        if is_json_field:
            casted_field = cast(field, String).label("value")
            stmt = select(distinct(casted_field)).order_by(casted_field)
        else:
            stmt = select(distinct(field)).order_by(field)

        if page and per_page:
            stmt = stmt.limit(per_page).offset((page - 1) * per_page)

        result = await self._session.scalars(stmt)
        values = result.unique().all()

        return values

    async def total_rows_for_values(self, name: str) -> int:
        return await self.count_rows_with_filter(self.MODEL, name)

    def is_enum_field(self, field: InstrumentedAttribute) -> bool:
        try:
            return isinstance(field.property.columns[0].type, SAEnum)
        except (AttributeError, IndexError):
            return False

    def get_enum_class(self, field: InstrumentedAttribute):
        if self.is_enum_field(field):
            return field.property.columns[0].type.enum_class
        return None

    async def count_rows_with_filter(
        self,
        model: Type[Base],
        name: str,
    ) -> int:
        field: InstrumentedAttribute = getattr(model, name)
        is_json_field = isinstance(field.type, JSON)

        if is_json_field:
            field = cast(field, String)

        stmt = select(func.count(field.distinct())).select_from(model)
        result = await self._session.scalar(stmt)
        return result or 0

    ###############
    ### Getters ###
    ###############

    async def get_by_id(self, model_id: int) -> TModel:
        model = await self._session.get(self.MODEL, model_id)
        if not model:
            raise APIException(
                code=404, message=f"Объект модели `{self.MODEL.__tablename__}` c id={model_id} не найден"
            )
        return self.convert_to_entity(model)

    async def get_list(
        self,
        per_page: int | None = None,
        page: int | None = None,
    ) -> list:
        stmt = select(self.MODEL)

        if page and per_page:
            stmt = stmt.limit(per_page).offset((page - 1) * per_page)

        result = await self._session.scalars(stmt.order_by(getattr(self.MODEL, "id").desc()))

        objects = result.all()
        return [self.LIST_DTO(**vars(obj)) for obj in objects]

    async def get_list_by_ids(
        self,
        id_list: list[int],
    ) -> list:
        if not id_list:
            return []

        stmt = select(self.MODEL).where(self.MODEL.id.in_(id_list))

        result = await self._session.scalars(stmt)
        objects = result.all()

        return [self.convert_to_entity(model) for model in objects]

    async def filter_by_id_list(self, id_list: list[int]) -> list[TModel]:
        stmt = select(self.MODEL).filter(getattr(self.MODEL, "id").in_(id_list))
        result = await self._session.scalars(stmt)
        return [self.convert_to_entity(row) for row in result.all()]

    ################
    ### Creators ###
    ################

    async def create(self, data: TModel) -> TModel:
        model = self.convert_to_model(data)
        self._session.add(model)
        await self._session.flush()
        return self.convert_to_entity(model)

    async def bulk_create(self, data: list[TModel]) -> list:
        models = [self.convert_to_model(entity) for entity in data]
        self._session.add_all(models)
        await self._session.flush(models)
        return [self.convert_to_entity(model) for model in models]

    ################
    ### Updators ###
    ################

    async def update(self, data: TModel) -> None:
        await self.bulk_update([data])

    async def bulk_update(self, entities: list[TModel]) -> None:
        models = [self.convert_to_model(entity) for entity in entities]
        await self._session.execute(update(self.MODEL), [vars(model) for model in models])

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
    async def delete_by_id(self, model_id: int) -> None:
        model = await self._session.get(self.MODEL, model_id)
        if not model:
            raise APIException(
                code=404, message=f"Объект модели `{self.MODEL.__tablename__}` c id={model_id} не найден"
            )
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

    async def all_exist_by_id_list(self, id_lst: list) -> bool:
        """Проверяет, существуют ли все объекты из списка id"""
        if not id_lst:
            return False

        stmt = select(func.count(self.MODEL.id)).where(self.MODEL.id.in_(id_lst))
        result = await self._session.scalar(stmt)
        return result == len(id_lst)

    async def check_is_exists_by_name(self, name: str) -> bool:
        pass
