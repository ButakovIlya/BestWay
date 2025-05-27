from abc import ABC, abstractmethod
from typing import Any


class AbstractNotifier(ABC):
    @abstractmethod
    async def send(self, channel: str, data: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def notify_user(self, user_id: int, event_type: str, data: dict[str, Any]) -> Any:
        pass

    @abstractmethod
    async def notify_general(self, event_type: str, data: dict[str, Any]) -> Any:
        pass
