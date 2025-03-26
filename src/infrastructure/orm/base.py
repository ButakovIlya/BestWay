from typing import Generic, Type, List, TypeVar

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from config.containers import Container
from config.exceptions import APIException
from infrastructure.models.alchemy.base import Base

TCreate = TypeVar("TCreate", bound=BaseModel)
TUpdate = TypeVar("TUpdate", bound=BaseModel)
TRead = TypeVar("TRead", bound=BaseModel)

class BaseViewSet(Generic[TCreate, TUpdate, TRead]):
    model: Type[Base]
    schema_read: Type[TRead]
    schema_create: Type[TCreate]
    schema_update: Type[TUpdate]
    prefix: str
    tags: list

    def __init__(self):
        self.router = APIRouter(prefix=self.prefix, tags=self.tags)

        self.router.add_api_route("/", self.list, response_model=List[self.schema_read], methods=["GET"])
        self.router.add_api_route("/{item_id}", self.get, response_model=self.schema_read, methods=["GET"])
        self.router.add_api_route("/", self.create, response_model=self.schema_read, methods=["POST"])
        self.router.add_api_route("/{item_id}", self.update, response_model=self.schema_read, methods=["PUT"])
        self.router.add_api_route("/{item_id}", self.delete, methods=["DELETE"])

    @inject
    async def list(
        self,
        session: AsyncSession = Depends(Provide[Container.db.session])
    ):
        result = await session.execute(select(self.model))
        return result.scalars().all()

    @inject
    async def get(
        self,
        item_id: int,
        session: AsyncSession = Depends(Provide[Container.db.session])
    ):
        result = await session.execute(select(self.model).where(self.model.id == item_id))
        obj = result.scalar_one_or_none()
        if not obj:
            raise APIException(code=404, message="Item not found")
        return obj

    @inject
    async def create(
        self,
        item_data: TCreate = Body(...),
        session: AsyncSession = Depends(Provide[Container.db.session])
    ):
        db_obj = self.model(**item_data.model_dump())
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @inject
    async def update(
        self,
        item_id: int,
        item_data: BaseModel = Body(...),
        session: AsyncSession = Depends(Provide[Container.db.session])
    ):
        result = await session.execute(select(self.model).where(self.model.id == item_id))
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise APIException(code=404, message="Item not found")
        
        for field, value in item_data.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    @inject
    async def delete(
        self,
        item_id: int,
        session: AsyncSession = Depends(Provide[Container.db.session])
    ):
        result = await session.execute(select(self.model).where(self.model.id == item_id))
        db_obj = result.scalar_one_or_none()
        if not db_obj:
            raise APIException(code=404, message="Item not found")
        
        await session.delete(db_obj)
        await session.commit()
        return {"detail": "Deleted"}
