import logging

from application.use_cases.routes.enums import RouteGenerationMode as Mode
from config.settings import Settings
from infrastructure.managers.ChatGPT.constants import FULL_MODE_PROMPT, PARTIAL_MODE_PROMPT
from infrastructure.managers.ChatGPT.dto import ChatGPTContentData

from .base import BaseClassificationManager

logger = logging.getLogger(__name__)


class ChatGPTRouteGenerationManager(BaseClassificationManager):
    """
    Класс, который занимается построением персонализированных маршрутов,
    используя ChatGPT.
    """

    settings = Settings()

    MAX_RESPONSES_PER_DAY = settings.chatgpt.max_responses_per_day or 300

    def __init__(self, serializer=None):
        super().__init__()
        self.serializer = serializer

    def generate_route(self, content: ChatGPTContentData, mode: Mode = Mode.FULL) -> dict:
        logger.info("_check_response_availability")
        self._check_response_availability()

        PROMPT: str = self._choose_prompt(mode)
        logger.info(f"_send_response to ChatGPT with prompt: {PROMPT}")
        logger.info(f"ChatGPT request body: {content.model_dump_json()}")
        response = self._send_request(content, PROMPT)
        self._increment_response()
        if self.serializer:
            return self.serializer(**response)

        logger.info(f"ChatGPT responded with a response: {response}")
        return response

    @staticmethod
    def _choose_prompt(mode: Mode = Mode.FULL) -> str:
        if mode == Mode.FULL:
            return FULL_MODE_PROMPT
        else:
            return PARTIAL_MODE_PROMPT
