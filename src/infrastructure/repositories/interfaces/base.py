from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import Result, ScalarResult

from domain.entities.model import Model

TModel = TypeVar("TModel", bound=Model)


class Repository(ABC):
    @abstractmethod
    def convert_to_model(self, entity: Any) -> Any:
        pass

    @abstractmethod
    def convert_to_entity(self, model: Any) -> Any:
        pass


class ModelRepository(Repository, Generic[TModel]):
    ENTITY: Type[Model]

    @abstractmethod
    def convert_to_model(self, entity: TModel) -> Any:
        pass

    @abstractmethod
    def convert_to_entity(self, model: Any) -> TModel:
        pass

    # CREATE
    @abstractmethod
    async def create(self, data: TModel) -> TModel:
        """Создать один объект"""
        pass

    @abstractmethod
    async def bulk_create(self, data: list[TModel]) -> list[TModel]:
        """Создать несколько объектов"""
        pass

    # READ
    @abstractmethod
    async def get_by_id(self, model_id: int) -> TModel:
        """Получить объект по ID"""
        pass

    @abstractmethod
    async def get_list(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TModel]:
        """Получить список объектов с возможностью фильтрации и пагинации"""
        pass

    @abstractmethod
    async def get_list_models(self, **filters) -> Result:
        """Получить список моделей объектов"""
        pass

    @abstractmethod
    async def get_list_by_ids(
        self,
        id_list: list[int],
    ) -> list[TModel]:
        """Получить список объектов по списку id"""
        pass

    @abstractmethod
    async def exists(self, **filters) -> bool:
        """Проверяет, существует ли объект с заданными параметрами"""
        pass

    @abstractmethod
    async def all_exist_by_id_list(self, id_lst: list) -> bool:
        """Проверяет, существуют ли все объекты из списка id"""
        pass

    # UPDATE
    @abstractmethod
    async def update(self, data: TModel) -> None:
        """Обновить объект по Entity"""
        pass

    @abstractmethod
    async def bulk_update(self, entities: list[TModel]) -> None:
        """Массовое обновление объектов"""
        pass

    # DELETE
    @abstractmethod
    async def delete(self, id_list: list[int]) -> list[int]:
        """Удалить объекты по списку ID"""
        pass

    @abstractmethod
    async def delete_by_id(self, model_id: int) -> None:
        """Удалить объект по ID"""
        pass

    @abstractmethod
    async def delete_all(self, scenario_id: int) -> None:
        """Удалить все объекты, относящиеся к конкретному сценарию"""
        pass

    @abstractmethod
    async def get_field_values(
        self,
        name: str,
        per_page: int | None = None,
        page: int | None = None,
    ) -> list[str]:
        pass

    @abstractmethod
    async def total_rows_for_values(
        self,
        name: str,
    ) -> int:
        pass
