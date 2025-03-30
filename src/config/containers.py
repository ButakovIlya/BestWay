from contextlib import asynccontextmanager
from types import ModuleType
from typing import AsyncGenerator

from dependency_injector import containers, providers
from redis.client import AbstractRedis  # type: ignore

from application.use_cases import UserCreateUseCase
from application.use_cases.auth.check_code import VerifySmsCodeUseCase
from application.use_cases.auth.phone_change import VerifyPhoneChangeSmsCodeUseCase
from application.use_cases.auth.send_code import SendSmsCodeUseCase
from application.use_cases.common import PhotoUpdateUseCase
from application.use_cases.models.field_values import ModelFieldValuesUseCase
from application.use_cases.places.photo import PlacePhotoUpdateUseCase
from application.use_cases.routes.create import RouteCreateUseCase
from application.use_cases.users.delete_user import UserDeleteUseCase
from application.use_cases.users.photo import UserPhotoUpdateUseCase
from application.use_cases.users.retrieve import UserRetrieveUseCase
from application.use_cases.users.update_user import UserUpdateUseCase
from config.settings import Settings
from infrastructure.managers.base import StorageManager
from infrastructure.managers.jwt_manager import JWTManager
from infrastructure.managers.local_storage import LocalStorageManager
from infrastructure.managers.sms_client import SmsClient
from infrastructure.redis import init_redis_pool
from infrastructure.redis.base import AbstractRedisCache
from infrastructure.redis.redis_cache import RedisCache
from infrastructure.repositories.alchemy.db import Database
from infrastructure.uow import SqlAlchemyUnitOfWork, UnitOfWork


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
        SmsClient, redis_cache=redis_cache, settings=settings.provided.sms
    )


class DBContainer(containers.DeclarativeContainer):
    settings = providers.Dependency(instance_of=Settings)

    db: providers.Provider[Database] = providers.Singleton(Database, settings=settings.provided.db)

    uow: providers.Provider[UnitOfWork] = providers.Factory(
        SqlAlchemyUnitOfWork, session_factory=db.provided.session_factory
    )

    session = providers.Factory(lambda db: db.session_factory(), db)


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

    # BASE

    # photos
    update_photo_use_case: providers.Provider[PhotoUpdateUseCase] = providers.Factory(
        PhotoUpdateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
    )

    # auth 
    send_code_use_case: providers.Provider[SendSmsCodeUseCase] = providers.Factory(
        SendSmsCodeUseCase, sms_client=clients.container.sms_client
    )

    verify_sms_code_use_case: providers.Provider[VerifySmsCodeUseCase] = providers.Factory(
        VerifySmsCodeUseCase,
        uow=db.container.uow,
        redis_client=clients.container.redis_cache,
        jwt_manager=jwt_manager,
    )

    change_number_sms_code_use_case: providers.Provider[VerifyPhoneChangeSmsCodeUseCase] = providers.Factory(
        VerifyPhoneChangeSmsCodeUseCase,
        uow=db.container.uow,
        redis_client=clients.container.redis_cache,
        jwt_manager=jwt_manager,
    )

    # users
    user_create_use_case: providers.Provider[UserCreateUseCase] = providers.Factory(
        UserCreateUseCase,
        uow=db.container.uow,
    )
    user_delete_use_case: providers.Provider[UserDeleteUseCase] = providers.Factory(
        UserDeleteUseCase,
        uow=db.container.uow,
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
        update_photo_use_case=update_photo_use_case,
    )

    # places
    place_avatar_update_use_case: providers.Provider[PlacePhotoUpdateUseCase] = providers.Factory(
        PlacePhotoUpdateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
        update_photo_use_case=update_photo_use_case,
    )

    # routes
    route_create_use_case: providers.Provider[RouteCreateUseCase] = providers.Factory(
        RouteCreateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
    )

    # models
    model_field_values_use_case: providers.Provider[ModelFieldValuesUseCase] = providers.Factory(
        ModelFieldValuesUseCase,
        uow=db.container.uow,
    )

    @classmethod
    @asynccontextmanager
    async def lifespan(cls, wireable_packages: list[ModuleType]) -> AsyncGenerator["Container", None]:
        container = cls()
        container.wire(packages=wireable_packages)
        yield container
