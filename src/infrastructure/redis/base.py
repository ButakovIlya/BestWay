from abc import abstractmethod

from redis.client import AbstractRedis  # type: ignore


class AbstractRedisCache:
    """Абстрактный класс для кеша в Redis."""

    TTL = 60 * 60 * 24  # 1 день

    def __init__(
        self,
        cache_connection: AbstractRedis,
    ):
        self._cache_connection = cache_connection

    def set_cache_fields(
        self,
        phone: str,
    ) -> None:
        self.phone = phone

    @abstractmethod
    def get(self, key: str) -> str | None:
        """Абстрактный метод для получения данных из кеша."""
        pass

    @abstractmethod
    def set(self, key: str, value: str, ttl: int = TTL) -> None:
        """Абстрактный метод для записи данных в кеш."""
        pass

    @abstractmethod
    def get_code_by_phone(self, phone: str) -> str | None:
        """Получает код по телефону"""
        pass

    @abstractmethod
    def set_code_by_phone(self, phone: str, code: int, ttl: int = TTL) -> str | None:
        """Получает код по телефону"""
        pass

    @abstractmethod
    def delete_code_by_phone(self, phone: str) -> None:
        """Удаляет код по телефону"""
        pass
