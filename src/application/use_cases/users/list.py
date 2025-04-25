from typing import List

from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserDTO
from infrastructure.uow import UnitOfWork
from src.domain.entities.user import User


class UsersListUseCase(UseCase):
    """
    List users.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self) -> List[UserDTO]:
        async with self._uow(autocommit=True):
            users: List[User] = await self._uow.users.get_list()
        return list(UserDTO.model_validate(user) for user in users)
