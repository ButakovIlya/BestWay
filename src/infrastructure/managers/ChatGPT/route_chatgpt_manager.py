import logging

from config.settings import Settings
from infrastructure.managers.ChatGPT.constants import PROMPT_TEXT

from .base import BaseClassificationManager

logger = logging.getLogger(__name__)


class ChatClassificationManager(BaseClassificationManager):
    """
    Класс, который занимается построением персонализированных маршрутов,
    используя ChatGPT.
    """

    settings = Settings()

    MAX_RESPONSES_PER_DAY = settings.chatgpt.max_responses_per_day or 300

    def __init__(self, serializer=None):
        super().__init__()
        self.serializer = serializer

    def classify(self, text, mappings=None):
        logger.info(f"Received text from PHP:\n{text}")
        payload_mappings = mappings
        mappings = (
            self._normalize_mappings(payload_mappings)
            if payload_mappings
            else self._get_mappings_from_main_backend()
        )

        dynamic_prompt = self._generate_dynamic_prompt(mappings)

        logger.info("_check_response_availability")
        self._check_response_availability()

        logger.info("_send_response to ChatGPT")
        logger.info(f"_send_promt to ChatGPT: {dynamic_prompt}")
        response = self._send_request(text, dynamic_prompt)

        self._increment_response()
        if self.serializer:
            return self.serializer(**response)

        logger.info(f"Classification result: {response}")
        return response

    def _generate_dynamic_prompt(self) -> str:
        formatted_prompt = self._format_prompt_str()
        return formatted_prompt

    def _format_prompt_str() -> str:
        return PROMPT_TEXT.format()


ChatManager = ChatClassificationManager()
