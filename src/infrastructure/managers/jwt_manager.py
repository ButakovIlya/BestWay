import datetime
from enum import Enum

import jwt

from config.settings import JWTSettings
from infrastructure.managers.dto import UserCreateDTO
from infrastructure.permissions.enums import RoleEnum


class TokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class JWTManager:
    """Менеджер для работы с JWT-токенами."""

    def __init__(self, settings: JWTSettings):
        self.jwt_settigns = settings.jwt

    def create_access_token(self, data: UserCreateDTO) -> str:
        """Создает access token."""
        payload = self.create_payload(data, token_type=TokenType.ACCESS)
        return jwt.encode(payload, self.jwt_settigns.secret_key, algorithm=self.jwt_settigns.algorithm)

    def create_refresh_token(self, data: UserCreateDTO) -> str:
        """Создает refresh token."""
        payload = self.create_payload(data, token_type=TokenType.REFRESH)
        return jwt.encode(payload, self.jwt_settigns.secret_key, algorithm=self.jwt_settigns.algorithm)

    def verify_token(self, token: str) -> dict:
        """Проверяет и декодирует токен."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_settigns.secret_key,
                algorithms=[self.jwt_settigns.algorithm],
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")

    def create_payload(self, data: UserCreateDTO, token_type: TokenType) -> dict:
        if token_type == TokenType.REFRESH:
            expire = datetime.datetime.now() + datetime.timedelta(
                days=self.jwt_settigns.refresh_token_expire_days
            )
        else:
            expire = datetime.datetime.now() + datetime.timedelta(
                minutes=self.jwt_settigns.access_token_expire_minutes
            )
        return {
            "token_type": token_type.value,
            "phone": data.phone,
            "exp": expire,
            "user_id": data.user_id,
            "is_admin": data.is_admin,
            "role": RoleEnum.ADMIN if data.is_admin else RoleEnum.USER,
        }
