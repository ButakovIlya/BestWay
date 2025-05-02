from typing import Generic, Optional, Type, TypeVar
from urllib.parse import urlencode

from fastapi import Request
from pydantic import BaseModel

from domain.validators.dto import PaginatedResponse

T = TypeVar("T", bound=BaseModel)


class Paginator(Generic[T]):
    def __init__(self, schema_read: Type[T], pagination_class: Type[BaseModel] = PaginatedResponse):
        self.schema_read = schema_read
        self.pagination_class = pagination_class

    async def paginate(
        self,
        result,
        request: Request,
        page: int = 1,
        page_size: int = 10,
    ) -> BaseModel:
        items = result.unique().scalars().all()
        total = len(items)

        start = (page - 1) * page_size
        end = start + page_size
        paginated = items[start:end]

        paginated_data = [self.schema_read.model_validate(obj) for obj in paginated]

        base_url = str(request.url).split("?")[0]
        query_params = dict(request.query_params)

        def build_url(page_number: int) -> Optional[str]:
            if page_number < 1 or page_number > (total + page_size - 1) // page_size:
                return None
            params = {**query_params, "page": str(page_number), "page_size": str(page_size)}
            return f"{base_url}?{urlencode(params)}"

        return self.pagination_class(
            data=paginated_data,
            count=total,
            page=page,
            next=build_url(page + 1),
            previous=build_url(page - 1),
        )
