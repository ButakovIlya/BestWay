from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserCreateDTO, UserDTO
from domain.entities.user import User
from infrastructure.uow import UnitOfWork


class UserCreateUseCase(UseCase):
    """
    Create new user.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    async def execute(self, data: UserCreateDTO) -> UserDTO:
        async with self._uow(autocommit=True):
            user = await self._uow.users.create(User(**data.model_dump()))

        return UserDTO.model_validate(user)
