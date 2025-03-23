from typing import Any, Protocol


class Task(Protocol):
    def delay(*args: Any, **kwargs: Any) -> Any: ...
