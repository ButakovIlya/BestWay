from application.use_cases.users.delete_user import UserDeleteUseCase
from application.use_cases.users.dto import FullUserUpdateDTO, UserCreateDTO, UserDTO
from application.use_cases.users.create_user import UserCreateUseCase
from fastapi import Response, status

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from application.use_cases.users.retrieve import UserRetrieveUseCase
from application.use_cases.users.update_user import UserUpdateUseCase
from config.containers import Container
from domain.validators.base import PhoneNumberValidator

router = APIRouter(tags=["Users"], prefix="/users")


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
@inject
async def get_my_profile(
    user_id: int,
    use_case: UserRetrieveUseCase = Depends(Provide[Container.user_retrieve_use_case]),
) -> UserDTO:
    """Получить данные профиля"""
    return await use_case.execute(user_id=user_id)


@router.post("", status_code=status.HTTP_200_OK)
# @is_admin
@inject
async def create_user(
    data: UserCreateDTO,
    use_case: UserCreateUseCase = Depends(Provide[Container.user_create_use_case]),
) -> UserDTO:
    return await use_case.execute(data=data)


@router.delete("/{phone}", status_code=status.HTTP_204_NO_CONTENT)
# @is_admin
@inject
async def delete_user(
    phone: str,
    use_case: UserDeleteUseCase = Depends(Provide[Container.user_delete_use_case]),
) -> Response:
    validated_phone = PhoneNumberValidator.validate_phone(phone)
    await use_case.execute(phone=validated_phone)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
# @is_admin
@inject
async def update_user(
    user_id: int,
    data: FullUserUpdateDTO,
    use_case: UserUpdateUseCase = Depends(Provide[Container.user_update_use_case]),
) -> UserDTO:
    return await use_case.execute(user_id=user_id, data=data)
