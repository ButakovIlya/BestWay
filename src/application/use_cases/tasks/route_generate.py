import logging
from typing import Any

from application.use_cases.base import UseCase
from application.use_cases.routes.enums import RouteGenerationMode as Mode
from common.exceptions import APIException
from infrastructure.redis.base import AbstractRedisCache
from infrastructure.tasks import Task
from infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)


class StartChatGPTRouteGenerateTaskUseCase(UseCase):
    def __init__(
        self,
        uow: UnitOfWork,
        redis_client: AbstractRedisCache,
        route_generate_gpt_task: Task,
    ) -> None:
        self._uow = uow
        self._redis_cache = redis_client
        self._chatgpt_process_route_task = route_generate_gpt_task

    async def execute(self, user_id: int, survey_id: int, mode: Mode = Mode.FULL) -> Any:
        if self._redis_cache.check_if_user_has_active_route_geration(user_id):
            raise APIException(code=400, message="У пользователя уже есть активная генерация маршрута")
        else:
            self._redis_cache.set_active_route_geration(user_id)

        logger.info("Started ChatGPT route generating task")
        self._chatgpt_process_route_task.delay(user_id, survey_id, mode.value)
