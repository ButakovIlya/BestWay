import jwt
import datetime
from typing import Any

from config.settings import JWTSettings

class JWTManager:
    """Менеджер для работы с JWT-токенами."""

    def __init__(self, settings: JWTSettings):
        self.jwt_settigns = settings.jwt

    def create_access_token(self, subject: Any, user_id: int) -> str:
        """Создает access token."""
        expire = datetime.datetime.now() + datetime.timedelta(
            minutes=self.jwt_settigns.access_token_expire_minutes
        )

        payload = {
            "token_type": "access",
            "sub": str(subject),
            "exp": expire,
            "user_id": user_id
        }
        return jwt.encode(
            payload,
            self.jwt_settigns.secret_key, 
            algorithm=self.jwt_settigns.algorithm
        )

    def create_refresh_token(self, subject: Any, user_id: int) -> str:
        """Создает refresh token."""
        expire = datetime.datetime.now() + datetime.timedelta(
            days=self.jwt_settigns.refresh_token_expire_days
        )
        payload = {
            "token_type": "refresh",
            "sub": str(subject),
            "exp": expire,
            "user_id": user_id
        }
        return jwt.encode(
            payload,
            self.jwt_settigns.secret_key, 
            algorithm=self.jwt_settigns.algorithm
        )

    def verify_token(self, token: str) -> dict:
        """Проверяет и декодирует токен."""
        try:
            payload = jwt.decode(token, self.jwt_settigns.secret_key, algorithms=[self.jwt_settigns.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token")
