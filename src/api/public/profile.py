from io import BytesIO
from typing import Optional
from api.permissions.is_authenticated import is_authenticated
from application.use_cases.users.dto import UserDTO, UserPhotoDTO, UserUpdateDTO
from application.use_cases.users.photo import UserPhotoUpdateUseCase
from application.use_cases.users.retrieve import UserRetrieveUseCase
from fastapi import File, UploadFile, status

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from application.use_cases.users.update_user import UserUpdateUseCase
from config.containers import Container

router = APIRouter(tags=["Profile"], prefix="/profile")


@router.get("", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def get_my_profile(
    request: Request,
    use_case: UserRetrieveUseCase = Depends(Provide[Container.user_retrieve_use_case]),
) -> UserDTO:
    """Получить данные профиля"""
    user_id: int = request.state.user.id
    return await use_case.execute(user_id=user_id)


@router.put("", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def update_my_profile(
    request: Request,
    data: UserUpdateDTO,
    use_case: UserUpdateUseCase = Depends(Provide[Container.user_update_use_case])
) -> UserDTO:
    """Обновить данные профиля"""
    user_id = request.state.user.id

    return await use_case.execute(user_id=user_id, data=data)


@router.post("/photo", status_code=status.HTTP_200_OK)
@is_authenticated
@inject
async def update_my_profile_photo(
    request: Request,
    photo: Optional[UploadFile] = File(None),
    use_case: UserPhotoUpdateUseCase = Depends(Provide[Container.user_photo_update_use_case])
) -> UserDTO:
    """Сменить фото профиля"""
    user_id = request.state.user.id

    data = UserPhotoDTO(
        filename=photo.filename if photo else None,
        photo=BytesIO(await photo.read()) if photo else None
    )
    return await use_case.execute(user_id=user_id, data=data)

