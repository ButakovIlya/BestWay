from datetime import datetime, timezone
from typing import Any, Awaitable, Callable

import jwt
from fastapi import Request
from jwt import ExpiredSignatureError
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from api.middlewares.exceptions import AuthenticationError, TokenExpiredError
from api.schemas import UserDTO
from config.settings import Settings
from domain.entities.user import User


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
        except (AuthenticationError, TokenExpiredError) as e:
            return JSONResponse(
                status_code=401,
                content={
                    "error": {
                        "code": e.code,
                        "message": e.message,
                        "detail": e.get_detail(),
                        "help_link": None,
                    }
                },
            )
        return await call_next(request)

    async def _get_user(self, request: Request) -> User | None:
        authorization = request.headers.get("Authorization")
        if not authorization:
            return None

        try:
            scheme, token = authorization.split()
        except ValueError:
            raise AuthenticationError(detail="Malformed Authorization header.")

        if scheme.lower() != "bearer":
            raise AuthenticationError(detail="Expected 'Bearer' authentication scheme.")

        payload = self._decode_token(token)
        self._validate_token_type(payload)
        self._validate_expiration_time(payload)
        validated = self._validate_payload(payload)

        return User(
            id=validated.id,
            phone=validated.phone,
        )

    def _decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self.jwt_settings.secret_key,
                algorithms=[self.jwt_settings.algorithm],
            )
        except ExpiredSignatureError:
            raise TokenExpiredError(detail="Token expired at timestamp: {}", *["{}".format(datetime.now())])
        except jwt.PyJWTError as e:
            raise AuthenticationError(detail="JWT decoding failed: {}", *[str(e)])

    def _validate_token_type(self, payload: dict) -> None:
        token_type = payload.get("token_type")
        if token_type != "access":
            raise AuthenticationError(detail="Token type must be 'access', got '{}'", *[str(token_type)])

    def _validate_expiration_time(self, payload: dict) -> None:
        try:
            expiration_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
            current_time = datetime.now(tz=timezone.utc)
            if expiration_time < current_time:
                raise TokenExpiredError(detail="Token expired at: {}", *[str(expiration_time)])
        except KeyError:
            raise AuthenticationError(detail="Token does not contain 'exp' claim.")

    def _validate_payload(self, payload: dict) -> UserDTO:
        try:
            return UserDTO(**payload)
        except ValidationError as e:
            raise AuthenticationError(detail="Invalid token payload: {}", *[str(e)])
