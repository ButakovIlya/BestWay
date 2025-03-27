from redis import Redis  # type: ignore

from infrastructure.redis.base import AbstractRedisCache


class RedisCache(AbstractRedisCache):
    """Реализация кеша на основе Redis"""

    def __init__(self, cache_connection: Redis):
        super().__init__(cache_connection)  # type: ignore
        self._cache_connection: Redis = cache_connection  # type: ignore

    def get(self, key: str) -> str | None:
        """Получает значение по ключу из Redis"""
        return self._cache_connection.get(key)

    def set(self, key: str, value: str, ttl: int = AbstractRedisCache.TTL) -> None:
        """Записывает значение в Redis с TTL"""
        self._cache_connection.setex(key, ttl, value)

    def get_code_by_phone(self, phone: str) -> str | None:
        """Получает код по телефону"""
        key = f"sms_code:{phone}"
        value = self._cache_connection.get(key)
        return value.decode("utf-8") if value else None

    def set_code_by_phone(self, phone: str, code: int, ttl: int = AbstractRedisCache.TTL) -> str | None:
        """Сохраняет код по телефону"""
        key = f"sms_code:{phone}"
        self._cache_connection.setex(key, ttl, code)

    def delete_code_by_phone(self, phone: str) -> None:
        """Удаляет код по телефону"""
        keys = [f"sms_code:{phone}"]
        self._cache_connection.delete(*keys)
