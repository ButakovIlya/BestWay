from io import BytesIO
from api.permissions.is_authenticated import is_authenticated
from api.public.schemas import UserUpdateForm
from application.use_cases.users.dto import UserDTO, UserUpdateDTO
from application.use_cases.users.retrieve import UserRetrieveUseCase
from fastapi import status

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from application.use_cases.users.update import UserUpdateUseCase
from config.containers import Container
from infrastructure.models.alchemy.users import User

router = APIRouter(tags=["/Profile"], prefix="/profile")


@router.get("", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def get_my_profile(
    request: Request,
    use_case: UserRetrieveUseCase = Depends(Provide[Container.user_retrieve_use_case]),
) -> UserDTO:
    user_id: int = request.state.user.id
    return await use_case.execute(user_id=user_id)


@router.put("", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def update_my_profile(
    request: Request,
    form: UserUpdateForm = Depends(),
    use_case: UserUpdateUseCase = Depends(Provide[Container.user_update_use_case])
):
    user_id = request.state.user.id

    # Валидация и сбор DTO
    data = UserUpdateDTO(
        first_name=form.first_name,
        email=form.email,
        phone=form.phone,
        photo=BytesIO(await form.photo.read()) if form.photo else None,
        filename=form.photo.filename if form.photo else None,
    )

    return await use_case.execute(user_id=user_id, data=data)


@router.delete("", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def get_my_profile(
    request: Request,
    use_case: UserRetrieveUseCase = Depends(Provide[Container.user_retrieve_use_case]),
) -> UserDTO:
    user_id: int = request.state.user.id
    return await use_case.execute(user_id=user_id)
