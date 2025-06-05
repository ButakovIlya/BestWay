from math import ceil
from typing import Generic, Optional, Type, TypeVar
from urllib.parse import urlencode

from fastapi import Request
from sqlalchemy import Result

from domain.validators.dto import PaginatedResponse

T = TypeVar("T")


class Paginator(Generic[T]):
    def __init__(self, schema_read: Type[T]):
        self.schema_read = schema_read

    async def paginate(
        self,
        result: Result,
        request: Request,
        page: int = 1,
        page_size: int = 10,
    ) -> PaginatedResponse[T]:
        items = result.scalars().unique().all()
        total_items = len(items)
        total_pages = ceil(total_items / page_size) if total_items else 1

        start = (page - 1) * page_size
        end = start + page_size
        paginated_items = items[start:end]
        data = [self.schema_read.model_validate(obj) for obj in paginated_items]

        base_url = str(request.url.replace_query_params())
        query_params = dict(request.query_params)

        def build_url(page_num: int) -> Optional[str]:
            if page_num < 1 or page_num > total_pages:
                return None
            params = {**query_params, "page": str(page_num), "page_size": str(page_size)}
            return f"{base_url}?{urlencode(params)}"

        return PaginatedResponse[T](
            data=data,
            count=total_items,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            next=build_url(page + 1),
            previous=build_url(page - 1),
        )
