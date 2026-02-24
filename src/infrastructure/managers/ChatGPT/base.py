import datetime
import json
import logging
from time import sleep
from typing import Any

import httpx

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
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content.model_dump_json()},
            ],
            "max_output_tokens": 60000,
            "truncation": "auto",
        }

    def _parse_chatgpt_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        Парсит ответ Responses API.
        Ожидаем JSON-строку в output_text (или в output[].content[].text).
        """
        logger.info(f"Received response from OpenAI API: {response.json()}")

        response.raise_for_status()
        data = response.json()

        response_content: str | None = data.get("output_text")

        if not response_content:
            parts = []
            for out_item in data.get("output", []) or []:
                for c in (out_item.get("content", []) or []):
                    if isinstance(c, dict) and "text" in c:
                        parts.append(c["text"])
            response_content = "".join(parts).strip() if parts else None

        if not response_content:
            raise APIException(message=f"Empty response from OpenAI: {data}", code=400)

        response_content = response_content.strip()

        try:
            return json.loads(response_content)
        except Exception:
            raise APIException(message=f"OpenAI returned non-JSON content: {response_content}")

    @retry_on_status_code(code=429, max_retries=CHATGPT_MAX_REQUEST_RETRIES, delay=CHATGPT_REQUEST_DELAY)
    def _send_request(self, content, system_prompt: str) -> dict[str, Any]:
        """
        Делает запрос в OpenAI. Возвращает dict (распарсенный JSON, который вернула модель).
        """
        self._check_response_availability()
        sleep(self.CHATGPT_REQUEST_DELAY)

        payload = self._create_request_payload(content, system_prompt)

        try:
            response = self.proxy_client.post(
                "https://api.openai.com/v1/responses",
                json=payload,
                headers={
                    "Authorization": f"Bearer {self.settings.chatgpt.api_key}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code >= 400:
                logger.error("OpenAI error %s: %s", response.status_code, response.text)

            return self._parse_chatgpt_response(response)

        except httpx.ReadTimeout as ex:
            logger.error(f"OpenAI ReadTimeout: {str(ex)}")
            raise
        except httpx.HTTPError as ex:
            logger.error(f"HTTP error while sending request to OpenAI: {str(ex)}")
            raise
        except Exception as ex:
            logger.error(f"Error while sending the request to OpenAI: {str(ex)}")
            raise
