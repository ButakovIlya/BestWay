from typing import List, Type

from fastapi import Body, Depends, HTTPException, Request, status
from pydantic import BaseModel

from infrastructure.permissions.enums import RoleEnum


async def request_body_schema_from_self(request: Request, body: dict = Body(...)) -> BaseModel:
    self_instance = request.scope["route"].endpoint.__self__
    schema: Type[BaseModel] = self_instance.schema_create
    return schema(**body)


def role_required(min_roles: List[RoleEnum]):
    async def dependency(request: Request):
        role_str = getattr(getattr(request.state, "user", None), "role", None)
        if not role_str:
            raise HTTPException(status_code=401, detail="Unauthorized: no role in request")

        try:
            current_role = RoleEnum(role_str)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid role format")

        if min_roles:
            if not any(current_role.level() >= r.level() for r in min_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access forbidden: requires one of roles {[r.value for r in min_roles]}",
                )

    return dependency
