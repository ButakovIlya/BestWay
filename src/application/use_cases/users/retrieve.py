from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserRetrieveDTO, UserDTO
from domain.entities.user import User
from infrastructure.uow import UnitOfWork


class UserRetrieveUseCase(UseCase):
    """
    Retrieve user.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, user_id: int) -> UserDTO:
        async with self._uow(autocommit=True):
            user = await self._uow.users.get_by_id(user_id)

        return UserDTO.model_validate(user)
