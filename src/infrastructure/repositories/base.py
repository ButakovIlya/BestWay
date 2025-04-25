from abc import ABC, abstractmethod
from typing import Any, Type

from infrastructure.repositories.interfaces.photo import PhotoRepository
from infrastructure.repositories.interfaces.place import PlaceRepository
from infrastructure.repositories.interfaces.route import RouteRepository
from infrastructure.repositories.interfaces.user import UserRepository


class UnitOfWork(ABC):
    users: UserRepository
    places: PlaceRepository
    photos: PhotoRepository
    routes: RouteRepository

    def __call__(self, *args: Any, autocommit: bool, **kwargs: Any) -> "UnitOfWork":
        self._autocommit = autocommit
        return self

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: Type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()
        elif self._autocommit:
            await self.commit()
        await self.shutdown()

    @abstractmethod
    async def rollback(self) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        pass

    @abstractmethod
    async def shutdown(self) -> None:
        pass
