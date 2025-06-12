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

    def set_active_route_geration(self, user_id: int, ttl: int = AbstractRedisCache.TTL_MINIUTE) -> None:
        key = f"active_generation:{user_id}"
        self._cache_connection.setex(key, ttl, "1")  # строка вместо bool

    def unset_active_route_geration(self, user_id: int, ttl: int = AbstractRedisCache.TTL_MINIUTE) -> None:
        key = f"active_generation:{user_id}"
        self._cache_connection.setex(key, ttl, "0")  # строка вместо bool

    def check_if_user_has_active_route_geration(self, user_id: int) -> bool:
        key = f"active_generation:{user_id}"
        value = self._cache_connection.get(key)
        return value == b"1"
