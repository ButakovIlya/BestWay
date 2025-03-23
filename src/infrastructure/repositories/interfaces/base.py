from abc import ABC, abstractmethod
from typing import Any, Generic, Type, TypeVar


from domain.entities.resource import Resource


TResource = TypeVar("TResource", bound=Resource)


class Repository(ABC):
    @abstractmethod
    def convert_to_model(self, entity: Any) -> Any:
        pass

    @abstractmethod
    def convert_to_entity(self, model: Any) -> Any:
        pass


class ResourceRepository(Repository, Generic[TResource]):
    ENTITY: Type[Resource]

    @abstractmethod
    def convert_to_model(self, entity: TResource) -> Any:
        pass

    @abstractmethod
    def convert_to_entity(self, model: Any) -> TResource:
        pass

    # CREATE
    @abstractmethod
    async def create(self, data: TResource) -> TResource:
        """Создать один объект"""
        pass

    @abstractmethod
    async def bulk_create(self, data: list[TResource]) -> list[TResource]:
        """Создать несколько объектов"""
        pass

    # READ
    @abstractmethod
    async def get_by_id(self, resource_id: int) -> TResource:
        """Получить объект по ID"""
        pass

    @abstractmethod
    async def get_list(
        self,
        filters: dict[str, Any] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[TResource]:
        """Получить список объектов с возможностью фильтрации и пагинации"""
        pass

    @abstractmethod
    async def exists(self, **filters) -> bool:
        """Проверяет, существует ли объект с заданными параметрами"""
        pass

    # UPDATE
    @abstractmethod
    async def update(self, resource_id: int, data: dict[str, Any]) -> TResource:
        """Обновить объект по ID"""
        pass

    @abstractmethod
    async def bulk_update(
        self, data: list[dict[str, Any]], batch_size: int = 100000
    ) -> list[TResource]:
        """Массовое обновление объектов"""
        pass

    # DELETE
    @abstractmethod
    async def delete(self, id_list: list[int]) -> list[int]:
        """Удалить объекты по списку ID"""
        pass

    @abstractmethod
    async def delete_by_id(self, resource_id: int) -> None:
        """Удалить объект по ID"""
        pass

    @abstractmethod
    async def delete_all(self, scenario_id: int) -> None:
        """Удалить все объекты, относящиеся к конкретному сценарию"""
        pass
