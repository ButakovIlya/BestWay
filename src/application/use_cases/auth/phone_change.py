from fastapi import HTTPException

from application.use_cases.auth.dto import ChangePhoneSmsPayloadDTO, TokenDTO
from application.use_cases.base import UseCase
from common.exceptions import APIException
from domain.entities.user import User
from infrastructure.managers.dto import UserCreateDTO
from infrastructure.managers.jwt_manager import JWTManager
from infrastructure.redis.redis_cache import RedisCache
from infrastructure.repositories.base import UnitOfWork


class VerifyPhoneChangeSmsCodeUseCase(UseCase):
    """Use Case для проверки SMS-кода для смены телефона и выдачи токенов."""

    def __init__(self, uow: UnitOfWork, redis_client: RedisCache, jwt_manager: JWTManager) -> None:
        self._uow = uow
        self._redis_cache = redis_client
        self._jwt_manager = jwt_manager

    async def execute(self, data: ChangePhoneSmsPayloadDTO) -> TokenDTO:
        """Проверяет код из SMS и выдает токены."""
        stored_code = self._redis_cache.get_code_by_phone(data.phone)

        if not stored_code or stored_code != data.code:
            raise HTTPException(status_code=400, detail="Неверный код")

        # Удаляем код после успешной проверки
        self._redis_cache.delete_code_by_phone(data.phone)

        async with self._uow(autocommit=True):
            if await self._uow.users.exists(phone=data.phone):
                user: User = await self._uow.users.get_by_phone(phone=data.phone)
                if not await self._uow.users.exists(phone=data.new_phone):
                    user.phone = data.new_phone
                    await self._uow.users.update(user)
                else:
                    raise APIException(
                        code=403,
                        message=f"Пользователь с телефоном '{data.new_phone}' уже существует"
                    )
            else:
                raise APIException(
                    code=404,
                    message=f"Пользователь с телефоном '{data.phone}' не найден"
                )
        # Генерация токенов
        data = UserCreateDTO(user_id=user.id, phone=user.phone, is_admin=user.is_admin)
        access_token = self._jwt_manager.create_access_token(data)
        refresh_token = self._jwt_manager.create_refresh_token(data)

        return TokenDTO(access_token=access_token, refresh_token=refresh_token)
