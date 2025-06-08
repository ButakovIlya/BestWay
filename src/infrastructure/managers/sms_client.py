import random
import time

import httpx
from fastapi import HTTPException

from application.use_cases.auth.dto import SmsPayloadDTO
from config.settings import SmsSettings
from domain.validators.base import PhoneNumberValidator
from infrastructure.redis.base import AbstractRedisCache


class SmsClient:
    """Менеджер для отправки SMS и кеширования кодов подтверждения."""

    SPAM_ATTEMPT_KEY_PREFIX: str = "sms_attempts:"
    SPAM_TIMESTAMP_KEY: str = "sms_last_attempt:"
    MAX_ATTEMPTS: int = 5000
    COOLDOWN_SECONDS: int = 1  # 5 минут
    BLOCK_SECONDS: int = 24 * 60 * 60  # 1 день

    def __init__(self, redis_cache: AbstractRedisCache, settings: SmsSettings):
        self._redis_cache = redis_cache
        self.settings = settings

    async def send_sms(self, payload: SmsPayloadDTO):
        """Отправляет SMS с кодом через внешний сервис."""
        self._validate_phone(payload.phone)
        headers, json_payload = self._build_payload(payload)

        async with httpx.AsyncClient() as client:
            try:
                pass
                # response = await client.post(
                #     self.settings.service_url,
                #     json=json_payload,
                #     headers=headers,
                #     timeout=10  # Ограничение по времени запроса
                # )
                # return self._handle_response(response)

            except httpx.RequestError as exc:
                raise HTTPException(status_code=500, detail=f"Ошибка сети: {str(exc)}")

    async def get_code(self, phone: str) -> str:
        """Генерирует или получает кешированный код подтверждения."""
        phone = self._validate_phone(phone)
        self._check_spam_restrictions(phone)

        code = self._generate_code()
        self._redis_cache.set_code_by_phone(phone, code, self.settings.cache_timeout)
        self._increment_sms_attempt(phone)

        return code

    def _build_payload(self, payload: SmsPayloadDTO) -> tuple[dict, list[dict]]:
        """Формирует headers и JSON payload для запроса."""
        headers = {
            "Authorization": f"Basic {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        json_payload = [
            {
                "channelType": "SMS",
                "senderName": "sms_promo",
                "destination": payload.phone,
                "content": f"Ваш код:{payload.code}",
            }
        ]
        return headers, json_payload

    @staticmethod
    def _generate_code() -> str:
        """Генерирует 4-значный код подтверждения."""
        return str(random.randint(1000, 9999))

    @staticmethod
    def _validate_phone(phone: str) -> str:
        """Проверяет номер телефона перед отправкой."""
        validator = PhoneNumberValidator(phone=phone)
        return validator.phone

    @staticmethod
    def _validate_response(response: httpx.Response):
        """Обрабатывает ошибки при отправке SMS."""
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Ошибка отправки SMS: {response.text}")

    def _handle_response(self, response: httpx.Response) -> dict:
        """Обрабатывает HTTP-ответ и возвращает результат."""
        if response.status_code == 200:
            try:
                data = response.json()
                if not data.get("success"):  # Проверка бизнес-логики API
                    raise HTTPException(
                        status_code=400,
                        detail=f"Ошибка отправки: {data.get('message')}",
                    )
                return {"message": "SMS отправлено", "response": data}

            except ValueError:
                raise HTTPException(status_code=500, detail="Ошибка обработки ответа API")

        elif response.status_code == 400:
            raise HTTPException(status_code=400, detail="Некорректные параметры запроса")

        elif response.status_code == 401:
            raise HTTPException(status_code=401, detail="Ошибка авторизации в SMS API")

        elif response.status_code == 429:
            raise HTTPException(status_code=429, detail="Превышен лимит SMS")

        elif response.status_code >= 500:
            raise HTTPException(status_code=500, detail="Ошибка на стороне SMS-сервиса")

        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Неизвестная ошибка: {response.text}",
            )

    def _check_spam_restrictions(self, phone: str) -> None:
        """Проверяет ограничения по частоте отправки кодов"""
        attempts_key = f"{self.SPAM_ATTEMPT_KEY_PREFIX}{phone}"
        timestamp_key = f"{self.SPAM_TIMESTAMP_KEY}{phone}"

        attempts = self._redis_cache.get(attempts_key)
        attempts = int(attempts) if attempts else 0

        last_ts = self._redis_cache.get(timestamp_key)
        now = int(time.time())

        if attempts >= self.MAX_ATTEMPTS:
            if last_ts and now - int(last_ts) < self.BLOCK_SECONDS:
                raise HTTPException(
                    status_code=429,
                    detail="Превышен лимит отправок. Попробуйте через 24 часа.",
                )
            else:
                self._redis_cache.set(attempts_key, "0")  # Сбросить счётчик

        elif attempts >= 2:
            if last_ts and now - int(last_ts) < self.COOLDOWN_SECONDS:
                raise HTTPException(
                    status_code=429,
                    detail="Слишком часто запрашиваете код. Попробуйте через 5 минут.",
                )

    def _increment_sms_attempt(self, phone: str) -> None:
        """Увеличивает счётчик отправок и обновляет время последней попытки"""
        attempts_key = f"{self.SPAM_ATTEMPT_KEY_PREFIX}{phone}"
        timestamp_key = f"{self.SPAM_TIMESTAMP_KEY}{phone}"

        attempts = self._redis_cache.get(attempts_key)
        attempts = int(attempts) if attempts else 0
        self._redis_cache.set(attempts_key, str(attempts + 1), ttl=self.BLOCK_SECONDS)
        self._redis_cache.set(timestamp_key, str(int(time.time())), ttl=self.BLOCK_SECONDS)
