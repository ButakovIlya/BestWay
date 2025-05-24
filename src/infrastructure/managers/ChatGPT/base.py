import datetime
import json
import logging
from time import sleep

from openai import OpenAI

from common.exceptions import APIException, ResponsesLimitExceededException
from config.settings import Settings
from infrastructure.managers.ChatGPT.dto import ChatGPTContentData
from infrastructure.managers.ChatGPT.utils import retry_on_status_code
from infrastructure.managers.proxy_client import ProxyClient
from infrastructure.repositories.interfaces.ChatGPT.base import ClassificationManager

logger = logging.getLogger(__name__)


class BaseClassificationManager(ClassificationManager):
    """
    Базовый класс, содержащий общую логику:
      - Повторные попытки при статусе 429
      - Работа с proxy_client
      - Общие методы _send_request (если нужно) и т.д.

    Лимиты и счётчики по дневным ограничениям.
    """

    settings = Settings()

    CHATGPT_MODEL = settings.chatgpt.model
    CHATGPT_REQUEST_DELAY = settings.chatgpt.request_delay
    CHATGPT_MAX_REQUEST_RETRIES = settings.chatgpt.max_request_retries
    MAX_RESPONSES_PER_DAY = settings.chatgpt.max_responses_per_day

    def __init__(self):

        self.proxy_client = ProxyClient(
            proxy_host=self.settings.proxy.host,
            proxy_http_port=self.settings.proxy.http_port,
            proxy_username=self.settings.proxy.username,
            proxy_password=self.settings.proxy.password,
        )
        self.proxy_openai_client = OpenAI(
            api_key=self.settings.chatgpt.api_key, http_client=self.proxy_client.client
        )

        self.responses_count = 0
        self.last_response_date = None

    def _check_daily_limit(self):
        """
        Проверяем, не превышен ли дневной лимит запросов (у наследника).
        """
        self._reset_counter_if_new_day()
        if self.responses_count >= self.MAX_RESPONSES_PER_DAY:
            raise ResponsesLimitExceededException()

    def _increment_response(self):
        """Увеличиваем счётчик обращений на 1."""
        self.responses_count += 1
        logger.info(f"Requests done: {self.responses_count}")

    def _reset_counter_if_new_day(self):
        """
        Обнуляем счётчик, если наступил новый день
        (каждый наследник делает это для своего счётчика).
        """
        current_date = datetime.date.today()
        if self.last_response_date != current_date:
            self.responses_count = 0
            self.last_response_date = current_date

    def is_max_responses_reached(self):
        self._reset_counter_if_new_day()
        return not self.responses_count < self.MAX_RESPONSES_PER_DAY

    def _check_response_availability(self):
        logger.info(f"Current response count from ChatGPT: {self.responses_count}.")
        if self.is_max_responses_reached():
            logger.info(
                f"Response count from ChatGPT ({self.responses_count}) "
                f"equal to daily limit ({self.MAX_RESPONSES_PER_DAY}), "
                f"try increase limits."
            )
            raise ResponsesLimitExceededException()

    def _create_request_payload(self, content: ChatGPTContentData, system_prompt: str) -> dict:
        """
        Формирует JSON-параметры (payload), которые будем отправлять в ChatGPT.
        """
        return {
            "model": self.CHATGPT_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content.model_dump_json()},
            ],
            "temperature": 0,
            "max_tokens": 2000,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }

    # TODO переделать валидацию
    def _parse_chatgpt_response(self, response: dict) -> dict:
        """
        Разбирает ответ от ChatGPT, пытается сначала интерпретировать
        как JSON, при неудаче – вернуть список объектов (или пустой).
        """
        logger.info("Received response from ChatGPT API")

        response_content = response.get("choices", [])[0].get("message", {}).get("content", [])
        logger.info(f"ChatGPT response_content: {response_content}")

        try:
            return json.loads(response_content)
        except Exception:
            logger.info("ChatGPT responded with non-JSON content")
            raise APIException(message=f"ChatGPT responded with non-JSON content: {str(response_content)}")

    @retry_on_status_code(code=429, max_retries=CHATGPT_MAX_REQUEST_RETRIES, delay=CHATGPT_REQUEST_DELAY)
    def _send_request(self, content: ChatGPTContentData, system_prompt: str) -> dict:
        try:
            self._check_response_availability()

            sleep(self.CHATGPT_REQUEST_DELAY)

            payload = self._create_request_payload(content, system_prompt)

            response = self.proxy_client.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {self.settings.chatgpt.api_key}"},
            )

            parsed_content = self._parse_chatgpt_response(response)

            return parsed_content
        except Exception as ex:
            logger.error(f"Error while sending the request to ChatGPT: {str(ex)}")
            raise ex
