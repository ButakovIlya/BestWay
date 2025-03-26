from application.use_cases.base import UseCase
from application.use_cases.users.dto import UserCreateDTO, UserDTO
from config.exceptions import APIException
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
            if not await self._uow.users.exists_by_phone(data.phone):
                user = await self._uow.users.create(User(**data.model_dump()))
            else:
                raise APIException(
                    code=400,
                    message=f"Пользователь с таким номером '{data.phone}' уже существует"
                )

        return UserDTO.model_validate(user)
