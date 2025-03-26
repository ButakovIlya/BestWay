from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from config.containers import Container


@inject
async def get_db_session(
    session_factory = Depends(Provide[Container.db.provided.session_factory]),
) -> AsyncGenerator[AsyncSession, None]:
    async_session_factory = session_factory
    async with async_session_factory() as session:
        yield session
