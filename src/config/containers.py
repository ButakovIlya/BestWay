from contextlib import asynccontextmanager
from types import ModuleType
from typing import AsyncGenerator

from dependency_injector import containers, providers
from redis.client import AbstractRedis  # type: ignore

from application.use_cases import UserCreateUseCase
from application.use_cases.auth.check_code import VerifySmsCodeUseCase
from application.use_cases.auth.phone_change import VerifyPhoneChangeSmsCodeUseCase
from application.use_cases.auth.send_code import SendSmsCodeUseCase
from application.use_cases.comments.create import CommentCreateUseCase
from application.use_cases.comments.edit import CommentEditUseCase
from application.use_cases.comments.remove import CommentRemoveUseCase
from application.use_cases.common import PhotoUpdateUseCase
from application.use_cases.common.create import ModelObjectCreateUseCase
from application.use_cases.common.delete import ModelObjectDeleteUseCase
from application.use_cases.common.list import ModelObjectListUseCase
from application.use_cases.common.partial_update import ModelObjectPartialUpdateUseCase
from application.use_cases.common.photo.delete import DeletePhotoUseCase
from application.use_cases.common.photo.upload import UploadPhotosUseCase
from application.use_cases.common.retrieve import ModelObjectRetrieveUseCase
from application.use_cases.common.update import ModelObjectUpdateUseCase
from application.use_cases.likes.create import LikeCreateUseCase
from application.use_cases.likes.remove import LikeRemoveUseCase
from application.use_cases.models.field_values import ModelFieldValuesUseCase
from application.use_cases.models.select_field_values import SelectFieldValuesUseCase
from application.use_cases.places.add_photos import PlacePhotosAddUseCase
from application.use_cases.places.avatar import PlacePhotoUpdateUseCase
from application.use_cases.places.create import PlaceCreateUseCase
from application.use_cases.places.feed import PlaceFeedListUseCase
from application.use_cases.posts.create import PostCreateUseCase
from application.use_cases.posts.feed import PostFeedFilterUseCase
from application.use_cases.routes.add_photos import RoutePhotosAddUseCase
from application.use_cases.routes.avatar import RoutePhotoUpdateUseCase
from application.use_cases.routes.chatgpt_create import ChatGPTRouteGenerateUseCase
from application.use_cases.routes.copy import RouteCopyUseCase
from application.use_cases.routes.create import RouteCreateUseCase
from application.use_cases.routes.feed.list import RouteFeedListUseCase
from application.use_cases.routes.feed.retrieve import RouteFeedRetrieveUseCase
from application.use_cases.routes.places.add import RoutePlaceAddUseCase
from application.use_cases.routes.places.remove import RoutePlaceRemoveUseCase
from application.use_cases.routes.places.update_order import RoutePlaceUpdateOrderUseCase
from application.use_cases.surveys.create import SurveyCreateUseCase
from application.use_cases.surveys.delete import SurveyDeleteUseCase
from application.use_cases.surveys.list import SurveysListUseCase
from application.use_cases.surveys.retrieve import SurveyRetrieveUseCase
from application.use_cases.surveys.update import SurveyUpdateUseCase
from application.use_cases.tasks.route_generate import StartChatGPTRouteGenerateTaskUseCase
from application.use_cases.users.delete_user import UserDeleteUseCase
from application.use_cases.users.list import UsersListUseCase
from application.use_cases.users.photo import UserPhotoUpdateUseCase
from application.use_cases.users.retrieve import UserRetrieveUseCase
from application.use_cases.users.update_user import UserUpdateUseCase
from config.settings import Settings
from infrastructure.managers.base import StorageManager
from infrastructure.managers.ChatGPT.route_chatgpt_manager import ChatGPTRouteGenerationManager
from infrastructure.managers.jwt_manager import JWTManager
from infrastructure.managers.local_storage import LocalStorageManager
from infrastructure.managers.sms_client import SmsClient
from infrastructure.notifications.notifier import PusherNotifier
from infrastructure.redis import init_redis_pool
from infrastructure.redis.base import AbstractRedisCache
from infrastructure.redis.redis_cache import RedisCache
from infrastructure.repositories.alchemy.db import Database
from infrastructure.tasks import Task
from infrastructure.tasks.routes import route_generate_gpt_task
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

    notifier: providers.Provider[PusherNotifier] = providers.Resource(
        PusherNotifier,
        app_id=settings.provided.pusher.app_id,
        key=settings.provided.pusher.key,
        secret=settings.provided.pusher.secret,
        cluster=settings.provided.pusher.cluster,
        ssl=True,
    )

    sms_client: providers.Provider[SmsClient] = providers.Resource(
        SmsClient, redis_cache=redis_cache, settings=settings.provided.sms
    )

    route_generate_gpt_manager: providers.Provider[ChatGPTRouteGenerationManager] = providers.Singleton(
        ChatGPTRouteGenerationManager,
    )


class DBContainer(containers.DeclarativeContainer):
    settings = providers.Dependency(instance_of=Settings)

    db: providers.Provider[Database] = providers.Singleton(Database, settings=settings.provided.db)

    uow: providers.Provider[UnitOfWork] = providers.Factory(
        SqlAlchemyUnitOfWork, session_factory=db.provided.session_factory
    )

    session = providers.Factory(lambda db: db.session_factory(), db)


class TasksContainer(containers.DeclarativeContainer):
    chatgpt_process_route: providers.Provider[Task] = providers.Singleton(lambda: route_generate_gpt_task)


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

    tasks = providers.Container(TasksContainer)

    ###################
    #### Use cases ####
    ###################

    # BASE

    # PHOTOS
    update_photo_use_case: providers.Provider[PhotoUpdateUseCase] = providers.Factory(
        PhotoUpdateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
    )

    delete_photo_use_case: providers.Provider[DeletePhotoUseCase] = providers.Factory(
        DeletePhotoUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
    )

    upload_photos_use_case: providers.Provider[UploadPhotosUseCase] = providers.Factory(
        UploadPhotosUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
    )

    # AUTH
    send_code_use_case: providers.Provider[SendSmsCodeUseCase] = providers.Factory(
        SendSmsCodeUseCase, sms_client=clients.container.sms_client
    )

    verify_sms_code_use_case: providers.Provider[VerifySmsCodeUseCase] = providers.Factory(
        VerifySmsCodeUseCase,
        uow=db.container.uow,
        redis_client=clients.container.redis_cache,
        jwt_manager=jwt_manager,
    )

    change_number_sms_code_use_case: providers.Provider[VerifyPhoneChangeSmsCodeUseCase] = (
        providers.Factory(
            VerifyPhoneChangeSmsCodeUseCase,
            uow=db.container.uow,
            redis_client=clients.container.redis_cache,
            jwt_manager=jwt_manager,
        )
    )

    # USERS
    user_create_use_case: providers.Provider[UserCreateUseCase] = providers.Factory(
        UserCreateUseCase,
        uow=db.container.uow,
    )

    user_delete_use_case: providers.Provider[UserDeleteUseCase] = providers.Factory(
        UserDeleteUseCase,
        uow=db.container.uow,
    )

    users_list_use_case: providers.Provider[UsersListUseCase] = providers.Factory(
        UsersListUseCase,
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

    # PLACES
    create_place_use_case: providers.Provider[PlaceCreateUseCase] = providers.Factory(
        PlaceCreateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
        update_photo_use_case=update_photo_use_case,
        upload_photos_use_case=upload_photos_use_case,
    )

    place_feed_use_case: providers.Provider[PlaceFeedListUseCase] = providers.Factory(
        PlaceFeedListUseCase,
        uow=db.container.uow,
    )

    place_avatar_update_use_case: providers.Provider[PlacePhotoUpdateUseCase] = providers.Factory(
        PlacePhotoUpdateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
        update_photo_use_case=update_photo_use_case,
    )

    place_photos_add_use_case: providers.Provider[PlacePhotosAddUseCase] = providers.Factory(
        PlacePhotosAddUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
        upload_photos_use_case=upload_photos_use_case,
    )

    # ROUTES
    route_create_use_case: providers.Provider[RouteCreateUseCase] = providers.Factory(
        RouteCreateUseCase,
        uow=db.container.uow,
    )

    route_place_add_use_case: providers.Provider[RoutePlaceAddUseCase] = providers.Factory(
        RoutePlaceAddUseCase,
        uow=db.container.uow,
    )

    route_place_remove_use_case: providers.Provider[RoutePlaceRemoveUseCase] = providers.Factory(
        RoutePlaceRemoveUseCase,
        uow=db.container.uow,
    )

    route_place_update_order_use_case: providers.Provider[RoutePlaceUpdateOrderUseCase] = providers.Factory(
        RoutePlaceUpdateOrderUseCase,
        uow=db.container.uow,
    )

    start_route_chatgpt_generate_task: providers.Provider[StartChatGPTRouteGenerateTaskUseCase] = (
        providers.Factory(
            StartChatGPTRouteGenerateTaskUseCase,
            uow=db.container.uow,
            redis_client=clients.container.redis_cache,
            route_generate_gpt_task=tasks.container.chatgpt_process_route,
        )
    )

    copy_route_use_case: providers.Provider[RouteCopyUseCase] = providers.Factory(
        RouteCopyUseCase,
        uow=db.container.uow,
    )

    route_chatgpt_generate_use_case: providers.Provider[ChatGPTRouteGenerateUseCase] = providers.Factory(
        ChatGPTRouteGenerateUseCase,
        uow=db.container.uow,
        redis_client=clients.container.redis_cache,
        notifier=clients.container.notifier,
        route_generate_gpt_manager=clients.container.route_generate_gpt_manager,
    )

    route_avatar_update_use_case: providers.Provider[RoutePhotoUpdateUseCase] = providers.Factory(
        RoutePhotoUpdateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
        update_photo_use_case=update_photo_use_case,
    )

    route_photos_add_use_case: providers.Provider[RoutePhotosAddUseCase] = providers.Factory(
        RoutePhotosAddUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
        upload_photos_use_case=upload_photos_use_case,
    )

    # MODELS
    model_field_values_use_case: providers.Provider[ModelFieldValuesUseCase] = providers.Factory(
        ModelFieldValuesUseCase,
        uow=db.container.uow,
    )
    select_field_values_use_case: providers.Provider[SelectFieldValuesUseCase] = providers.Factory(
        SelectFieldValuesUseCase,
    )

    # SURVEYS
    user_survey_create_use_case: providers.Provider[SurveyCreateUseCase] = providers.Factory(
        SurveyCreateUseCase,
        uow=db.container.uow,
    )
    user_survey_delete_use_case: providers.Provider[SurveyDeleteUseCase] = providers.Factory(
        SurveyDeleteUseCase,
        uow=db.container.uow,
    )

    users_survey_list_use_case: providers.Provider[SurveysListUseCase] = providers.Factory(
        SurveysListUseCase,
        uow=db.container.uow,
    )

    user_survey_retrieve_use_case: providers.Provider[SurveyRetrieveUseCase] = providers.Factory(
        SurveyRetrieveUseCase,
        uow=db.container.uow,
    )

    user_survey_update_use_case: providers.Provider[SurveyUpdateUseCase] = providers.Factory(
        SurveyUpdateUseCase,
        uow=db.container.uow,
    )

    # PUBLIC
    # ROUTES
    route_feed_use_case: providers.Provider[RouteFeedListUseCase] = providers.Factory(
        RouteFeedListUseCase,
        uow=db.container.uow,
    )
    route_feed_retrieve_use_case: providers.Provider[RouteFeedRetrieveUseCase] = providers.Factory(
        RouteFeedRetrieveUseCase,
        uow=db.container.uow,
    )

    # LIKES
    like_create_use_case: providers.Provider[LikeCreateUseCase] = providers.Factory(
        LikeCreateUseCase,
        uow=db.container.uow,
    )
    remove_like_use_case: providers.Provider[LikeRemoveUseCase] = providers.Factory(
        LikeRemoveUseCase,
        uow=db.container.uow,
    )

    # COMMENTS
    comment_create_use_case: providers.Provider[CommentCreateUseCase] = providers.Factory(
        CommentCreateUseCase,
        uow=db.container.uow,
    )
    remove_comment_use_case: providers.Provider[CommentRemoveUseCase] = providers.Factory(
        CommentRemoveUseCase,
        uow=db.container.uow,
    )
    edit_create_use_case: providers.Provider[CommentEditUseCase] = providers.Factory(
        CommentEditUseCase,
        uow=db.container.uow,
    )

    # POSTS
    create_post_use_case: providers.Provider[PostCreateUseCase] = providers.Factory(
        PostCreateUseCase,
        uow=db.container.uow,
        storage_manager=storage_manager,
        update_photo_use_case=update_photo_use_case,
    )

    post_feed_use_case: providers.Provider[PostFeedFilterUseCase] = providers.Factory(
        PostFeedFilterUseCase,
        uow=db.container.uow,
    )

    # COMMON CRUD USE_CASES
    object_create_use_case: providers.Provider[ModelObjectCreateUseCase] = providers.Factory(
        ModelObjectCreateUseCase,
        uow=db.container.uow,
    )

    object_retrieve_use_case: providers.Provider[ModelObjectRetrieveUseCase] = providers.Factory(
        ModelObjectRetrieveUseCase,
        uow=db.container.uow,
    )

    object_list_use_case: providers.Provider[ModelObjectListUseCase] = providers.Factory(
        ModelObjectListUseCase,
        uow=db.container.uow,
    )

    object_update_use_case: providers.Provider[ModelObjectUpdateUseCase] = providers.Factory(
        ModelObjectUpdateUseCase,
        uow=db.container.uow,
    )

    object_partial_update_use_case: providers.Provider[ModelObjectPartialUpdateUseCase] = providers.Factory(
        ModelObjectPartialUpdateUseCase,
        uow=db.container.uow,
    )

    object_delete_use_case: providers.Provider[ModelObjectDeleteUseCase] = providers.Factory(
        ModelObjectDeleteUseCase,
        uow=db.container.uow,
    )

    @classmethod
    @asynccontextmanager
    async def lifespan(cls, wireable_packages: list[ModuleType]) -> AsyncGenerator["Container", None]:
        container = cls()
        container.wire(packages=wireable_packages)
        yield container
