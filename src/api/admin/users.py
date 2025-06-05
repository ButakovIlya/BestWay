from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, Response, status

from api.permissions.is_admin import is_admin
from application.use_cases.users.create_user import UserCreateUseCase
from application.use_cases.users.delete_user import UserDeleteUseCase
from application.use_cases.users.dto import FullUserUpdateDTO, UserCreateDTO, UserDTO
from application.use_cases.users.list import UsersListUseCase
from application.use_cases.users.retrieve import UserRetrieveUseCase
from application.use_cases.users.update_user import UserUpdateUseCase
from config.containers import Container
from domain.validators.dto import PaginatedResponse

# router = APIRouter(tags=["Users"], prefix="/users", dependencies=[Depends(is_admin)])
router = APIRouter(tags=["Users"], prefix="/users")


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
@inject
async def retrieve_user(
    user_id: int,
    use_case: UserRetrieveUseCase = Depends(Provide[Container.user_retrieve_use_case]),
) -> UserDTO:
    """Получить данные профиля"""
    return await use_case.execute(user_id=user_id)


@router.get("/", response_model=PaginatedResponse[UserDTO], status_code=status.HTTP_200_OK)
@inject
async def list_users(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    use_case: UsersListUseCase = Depends(Provide[Container.users_list_use_case]),
) -> PaginatedResponse[UserDTO]:
    """Получить список пользователей с пагинацией"""
    return await use_case.execute(request=request, page=page, page_size=page_size)


@router.post("", status_code=status.HTTP_200_OK)
@inject
async def create_user(
    request: Request,
    data: UserCreateDTO,
    use_case: UserCreateUseCase = Depends(Provide[Container.user_create_use_case]),
) -> UserDTO:
    return await use_case.execute(data=data)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    user_id: int,
    use_case: UserDeleteUseCase = Depends(Provide[Container.user_delete_use_case]),
) -> Response:
    await use_case.execute(user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{user_id}", status_code=status.HTTP_200_OK)
@inject
async def update_user(
    user_id: int,
    data: FullUserUpdateDTO,
    use_case: UserUpdateUseCase = Depends(Provide[Container.user_update_use_case]),
) -> UserDTO:
    return await use_case.execute(user_id=user_id, data=data)
