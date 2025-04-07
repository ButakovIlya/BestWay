from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.enums import ModelType
from infrastructure.repositories.alchemy import (
    SqlAlchemyPhotosRepository,
    SqlAlchemyPlacesRepository,
    SqlAlchemyUsersRepository,
)
from infrastructure.repositories.interfaces.base import ModelRepository
from infrastructure.uow.base import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> UnitOfWork:
        self._session = self._session_factory()

        self.users = SqlAlchemyUsersRepository(self._session)
        self.places = SqlAlchemyPlacesRepository(self._session)
        self.photos = SqlAlchemyPhotosRepository(self._session)

        return await super().__aenter__()

    def get_model_repository(self, resource_name: ModelType) -> ModelRepository:
        print(resource_name)
        print(ModelType.PLACES.value)
        match resource_name:
            case ModelType.PLACES.value:
                return self.places

    async def rollback(self) -> None:
        await self._session.rollback()

    async def commit(self) -> None:
        await self._session.commit()

    async def shutdown(self) -> None:
        await self._session.close()
