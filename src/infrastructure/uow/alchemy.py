from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.entities.enums import ModelType
from infrastructure.repositories.alchemy import (
    SqlAlchemyPhotosRepository,
    SqlAlchemyPlacesRepository,
    SqlAlchemyUsersRepository,
)
from infrastructure.repositories.alchemy.comments import SqlAlchemyCommentsRepository
from infrastructure.repositories.alchemy.likes import SqlAlchemyLikesRepository
from infrastructure.repositories.alchemy.posts import SqlAlchemyPostsRepository
from infrastructure.repositories.alchemy.route_places import SqlAlchemyRoutePlacesRepository
from infrastructure.repositories.alchemy.routes import SqlAlchemyRoutesRepository
from infrastructure.repositories.alchemy.survey import SqlAlchemySurveysRepository
from infrastructure.repositories.interfaces.base import ModelRepository
from infrastructure.uow.base import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> UnitOfWork:
        self._session = self._session_factory()

        self.users = SqlAlchemyUsersRepository(self._session)
        self.places = SqlAlchemyPlacesRepository(self._session)
        self.routes = SqlAlchemyRoutesRepository(self._session)
        self.posts = SqlAlchemyPostsRepository(self._session)
        self.route_places = SqlAlchemyRoutePlacesRepository(self._session)
        self.surveys = SqlAlchemySurveysRepository(self._session)
        self.photos = SqlAlchemyPhotosRepository(self._session)

        self.comments = SqlAlchemyCommentsRepository(self._session)
        self.likes = SqlAlchemyLikesRepository(self._session)

        return await super().__aenter__()

    def get_model_repository(self, model_name: ModelType) -> ModelRepository:
        match model_name:
            case ModelType.PLACES:
                return self.places
            case ModelType.USERS:
                return self.users
            case ModelType.ROUTES:
                return self.routes
            case ModelType.POSTS:
                return self.posts
            case ModelType.COMMENTS:
                return self.comments
            case ModelType.LIKES:
                return self.likes
            case ModelType.SURVEYS:
                return self.surveys
            case _:
                raise ValueError(f"Repository not found: {model_name}")

    async def rollback(self) -> None:
        await self._session.rollback()

    async def commit(self) -> None:
        await self._session.commit()

    async def shutdown(self) -> None:
        await self._session.close()
