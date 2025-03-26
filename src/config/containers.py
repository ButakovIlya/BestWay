from contextlib import asynccontextmanager
from types import ModuleType
from typing import AsyncGenerator

from application.use_cases.auth.check_code import VerifySmsCodeUseCase
from application.use_cases.auth.send_code import SendSmsCodeUseCase
from application.use_cases.users.photo import UserPhotoUpdateUseCase
from application.use_cases.users.retrieve import UserRetrieveUseCase
from application.use_cases.users.update import UserUpdateUseCase
from config.settings import Settings

from infrastructure.managers.base import StorageManager
from infrastructure.managers.jwt_manager import JWTManager
from infrastructure.managers.local_storage import LocalStorageManager
from infrastructure.managers.sms_client import SmsClient
from infrastructure.uow import SqlAlchemyUnitOfWork, UnitOfWork
from infrastructure.repositories.alchemy.db import Database
from infrastructure.redis import init_redis_pool
from infrastructure.redis.base import AbstractRedisCache
from infrastructure.redis.redis_cache import RedisCache
from redis.client import AbstractRedis  # type: ignore

from dependency_injector import containers, providers

from application.use_cases import UserCreateUseCase


class ClientsContainer(containers.DeclarativeContainer):
    settings = providers.Dependency(instance_of=Settings)

    redis_pool: providers.Provider[AbstractRedis] = providers.Resource(
        init_redis_pool.init_redis_pool,  # type: ignore
        host=settings.provided.redis.host,
        password=settings.provided.redis.password,
    )

    redis_cache: providers.Provider[AbstractRedisCache] = providers.Resource(
        RedisCache,
        cache_connection=redis_pool,
    )

    sms_client: providers.Provider[SmsClient] = providers.Resource(
        SmsClient,
        redis_cache=redis_cache,
        settings=settings.provided.sms
    )


class DBContainer(containers.DeclarativeContainer):
    settings = providers.Dependency(instance_of=Settings)

    db: providers.Provider[Database] = providers.Singleton(
        Database, settings=settings.provided.db
    )

    uow: providers.Provider[UnitOfWork] = providers.Factory(
        SqlAlchemyUnitOfWork, session_factory=db.provided.session_factory
    )


class Container(containers.DeclarativeContainer):
    settings: providers.Provider[Settings] = providers.Singleton(Settings)

    db = providers.Container(DBContainer, settings=settings)

    clients = providers.Container(ClientsContainer, settings=settings)

    redis = providers.Container(DBContainer, settings=settings)

    jwt_manager = providers.Singleton(JWTManager, settings=settings)

    storage_manager: providers.Provider[StorageManager] = providers.Singleton(
        LocalStorageManager,
        settings=settings,
    )

    ###################
    #### Use cases ####
    ###################

    user_create_use_case: providers.Provider[UserCreateUseCase] = providers.Factory(
        UserCreateUseCase,
        uow=db.container.uow,
    )
    send_code_use_case: providers.Provider[SendSmsCodeUseCase]  = providers.Factory(
        SendSmsCodeUseCase,
        sms_client=clients.container.sms_client
    )

    verify_sms_code_use_case: providers.Provider[VerifySmsCodeUseCase] = providers.Factory(
        VerifySmsCodeUseCase,
        uow=db.container.uow,
        redis_client=clients.container.redis_cache,
        jwt_manager=jwt_manager
    )


    user_retrieve_use_case: providers.Provider[UserRetrieveUseCase] = providers.Factory(
        UserRetrieveUseCase,
        uow=db.container.uow,
    )

    user_update_use_case: providers.Provider[UserUpdateUseCase] = providers.Factory(
        UserUpdateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
    )

    user_photo_update_use_case: providers.Provider[UserPhotoUpdateUseCase] = providers.Factory(
        UserPhotoUpdateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
    )



    @classmethod
    @asynccontextmanager
    async def lifespan(
        cls, wireable_packages: list[ModuleType]
    ) -> AsyncGenerator["Container", None]:
        container = cls()
        container.wire(packages=wireable_packages)
        yield container
