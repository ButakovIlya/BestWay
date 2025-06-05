from fastapi import Request

from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserDTO
from domain.validators.dto import PaginatedResponse
from infrastructure.managers.paginator import Paginator
from infrastructure.uow import UnitOfWork


class UsersListUseCase(UseCase):
    """
    List users with pagination.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow
        self.paginator = Paginator(schema_read=UserDTO)

    async def execute(
        self, request: Request, page: int = 1, page_size: int = 10
    ) -> PaginatedResponse[UserDTO]:
        async with self._uow(autocommit=True):
            result = await self._uow.users.get_list_models()

        return await self.paginator.paginate(result, request, page, page_size)
