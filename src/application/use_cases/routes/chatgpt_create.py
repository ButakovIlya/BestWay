import logging
from typing import Any

from application.use_cases.base import UseCase
from infrastructure.tasks import Task
from infrastructure.uow import UnitOfWork

logger = logging.getLogger("actual_data")


class ChatGPTRouteCreateUseCase(UseCase):
    def __init__(
        self,
        uow: UnitOfWork,
        chatgpt_process_route_task: Task,
    ) -> None:
        self._uow = uow
        self._chatgpt_process_route_task = chatgpt_process_route_task

    async def execute(self) -> Any:
        logger.info("Start upload file use case")

        task_result = self._chatgpt_process_route_task.delay()
        logger.info("End upload file use case")
