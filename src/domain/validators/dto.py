from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    count: int
    page: int
    next: Optional[str] = None
    previous: Optional[str] = None
