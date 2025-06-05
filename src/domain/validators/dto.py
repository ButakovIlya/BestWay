from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    count: int  # Общее количество элементов
    page: int  # Текущая страница
    page_size: int  # Элементов на страницу
    total_pages: int  # Общее количество страниц
    next: Optional[str] = None
    previous: Optional[str] = None
