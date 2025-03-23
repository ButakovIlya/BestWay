from config.settings import DBSettings

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class Database:
    def __init__(self, settings: DBSettings) -> None:
        self._engine: AsyncEngine = create_async_engine(
            url=str(settings.dsn),
            pool_size=settings.pool_size,
            max_overflow=settings.max_overflow,
            echo=settings.echo,
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine, expire_on_commit=False
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory
