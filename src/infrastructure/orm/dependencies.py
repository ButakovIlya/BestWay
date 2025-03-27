from fastapi import Request, Body
from pydantic import BaseModel
from typing import Type

async def request_body_schema_from_self(request: Request, body: dict = Body(...)) -> BaseModel:
    self_instance = request.scope["route"].endpoint.__self__
    schema: Type[BaseModel] = self_instance.schema_create
    return schema(**body)
