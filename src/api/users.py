from application.use_cases.users.dto import UserCreateDTO, UserDTO
from application.use_cases.users.create import UserCreateUseCase
from fastapi import status

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Request

from config.containers import Container

router = APIRouter(tags=["Users"], prefix="/users")


@router.post("/create", status_code=status.HTTP_200_OK)
# @is_authenticated
@inject
async def create_user(
    request: Request,
    data: UserCreateDTO,
    use_case: UserCreateUseCase = Depends(Provide[Container.user_create_use_case]),
) -> UserDTO:
    return await use_case.execute(data=data)
