from fastapi import HTTPException
from domain.entities.user import User
from infrastructure.managers.jwt_manager import JWTManager
from application.use_cases.base import UseCase
from application.use_cases.auth.dto import SmsPayloadDTO, TokenDTO
from infrastructure.redis.redis_cache import RedisCache
from infrastructure.repositories.base import UnitOfWork


class VerifySmsCodeUseCase(UseCase):
    """Use Case для проверки SMS-кода и выдачи токенов."""

    def __init__(self, uow: UnitOfWork, redis_client: RedisCache, jwt_manager: JWTManager) -> None:
        self._uow = uow
        self._redis_cache = redis_client
        self._jwt_manager = jwt_manager

    async def execute(self, data: SmsPayloadDTO) -> TokenDTO:
        """Проверяет код из SMS и выдает токены."""
        stored_code = self._redis_cache.get_code_by_phone(data.phone)

        if not stored_code or stored_code != data.code:
            raise HTTPException(status_code=400, detail="Неверный код")

        # Удаляем код после успешной проверки
        self._redis_cache.delete_code_by_phone(data.phone)

        async with self._uow(autocommit=True):
            if await self._uow.users.exists(phone=data.phone):
                user = await self._uow.users.get_by_phone(phone=data.phone)
            else:
                user = await self._uow.users.create(
                    User(
                        phone=data.phone
                    )
                )
        # Генерация токенов
        access_token = self._jwt_manager.create_access_token(data.phone, user.id)
        refresh_token = self._jwt_manager.create_refresh_token(data.phone, user.id)

        return TokenDTO(
            access_token=access_token,
            refresh_token=refresh_token
        )
