from abc import ABC, abstractmethod
from typing import Any


class UseCase(ABC):
    """Base class for all use cases"""

    @abstractmethod
    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        pass
