from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

from api.middlewares.exceptions import AuthenticationError, TokenExpiredError
from api.schemas import UserDTO
from config.settings import Settings
from domain.entities.user import User

import jwt
from fastapi import Request
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response


class JwtTokenUserMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        *args: Any,
        settings: Settings,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.jwt_settings = settings.jwt

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        try:
            request.state.user = await self._get_user(request)
        except AuthenticationError as e:
            return JSONResponse(
                content={
                    "error": {
                        "code": e.code,
                        "msg": e.message,
                        "detail": None,
                        "help_link": None,
                    }
                }
            )
        return await call_next(request)

    async def _get_user(self, request: Request) -> User | None:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        payload = self._decode_token(token)
        self._validate_token_type(payload)
        self._validate_expiration_time(payload)
        validated = self._validate_payload(payload)
        return User(
            id=validated.id,
            phone=validated.phone
        )

    def _decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.jwt_settings.secret_key,
                algorithms=[self.jwt_settings.algorithm],
            )
        except jwt.PyJWTError:
            raise AuthenticationError()

    def _validate_token_type(self, payload: dict) -> None:
        token_type = payload.get("token_type")
        if not token_type or token_type != "access":
            raise AuthenticationError()

    def _validate_expiration_time(self, payload: dict) -> None:
        app_timezone = timezone.utc
        expiration_time = datetime.fromtimestamp(payload["exp"], tz=app_timezone)
        current_time = datetime.now(tz=app_timezone)
        if expiration_time < current_time:
            raise TokenExpiredError()

    def _validate_payload(self, payload: dict) -> UserDTO:
        try:
            return UserDTO(**payload)
        except ValidationError:
            raise AuthenticationError()
