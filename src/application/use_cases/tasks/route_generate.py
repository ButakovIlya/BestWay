import logging
from typing import Any

from application.use_cases.base import UseCase
from application.use_cases.routes.enums import RouteGenerationMode as Mode
from infrastructure.tasks import Task
from infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)


class StartChatGPTRouteGenerateTaskUseCase(UseCase):
    def __init__(
        self,
        uow: UnitOfWork,
        route_generate_gpt_task: Task,
    ) -> None:
        self._uow = uow
        self._chatgpt_process_route_task = route_generate_gpt_task

    async def execute(self, user_id: int, survey_id: int, mode: Mode = Mode.FULL) -> Any:
        logger.info("Started ChatGPT route generating task")
        self._chatgpt_process_route_task.delay(user_id, survey_id, mode.name)
