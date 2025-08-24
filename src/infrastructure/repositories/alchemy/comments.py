from typing import Any, List

from sqlalchemy import Result, desc, func, select
from sqlalchemy.orm import joinedload

from application.use_cases.comments.dto import CommentBaseDTO, CommentDTO
from common.exceptions import APIException
from domain.entities.comment import Comment
from infrastructure.models.alchemy.routes import Comment as CommentModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces import CommentRepository


class SqlAlchemyCommentsRepository(SqlAlchemyModelRepository[Comment], CommentRepository):
    MODEL = CommentModel
    ENTITY = Comment
    LIST_DTO = CommentDTO

    async def create(self, data: Comment) -> Comment:
        model = self.convert_to_model(data)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(
            model,
            attribute_names=["author", "route", "place"],
        )
        return self.convert_to_entity(model)

    async def count_by_user_and_object(self, data: CommentBaseDTO) -> int:
        stmt = select(func.count()).where(
            CommentModel.route_id == data.route_id,
            CommentModel.place_id == data.place_id,
            CommentModel.author_id == data.author_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_list_by_route_id(self, route_id: int) -> List[Comment]:
        result = await self._session.execute(select(CommentModel).where(CommentModel.route_id == route_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

    async def get_list_by_place_id(self, place_id: int) -> List[Comment]:
        result = await self._session.execute(select(CommentModel).where(CommentModel.place_id == place_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

    async def get_list_by_user_id(self, user_id: int) -> List[Comment]:
        result = await self._session.execute(select(CommentModel).where(CommentModel.author_id == user_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

    async def get_by_id(self, model_id: int, **filters: Any) -> Comment:
        """Получить комментарий по id и фильтрам"""
        filters_with_id = {"id": model_id, **filters}
        stmt = (
            select(CommentModel)
            .filter_by(**filters_with_id)
            .options(
                joinedload(CommentModel.author),
            )
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        if not model:
            raise APIException(code=404, message=f"Комментарий c id={model_id} не найден")
        return self.convert_to_entity(model)

    async def get_list_models(self, **filters: Any) -> Result:
        """Получить коментарии по фильтрам"""
        stmt = (
            select(CommentModel)
            .filter_by(**filters)
            .options(
                joinedload(CommentModel.author),
            )
            .order_by(desc(CommentModel.timestamp))
        )
        return await self._session.execute(stmt)

    def convert_to_model(self, entity: Comment) -> CommentModel:
        return CommentModel(
            id=entity.id,
            author_id=entity.author_id,
            route_id=entity.route_id,
            place_id=entity.place_id,
            timestamp=entity.timestamp,
            comment=entity.comment,
        )

    def convert_to_entity(self, model: CommentModel) -> Comment:
        return Comment(
            id=model.id,
            author_id=model.author_id,
            author=model.author,
            route_id=model.route_id,
            place_id=model.place_id,
            timestamp=model.timestamp,
            comment=model.comment,
        )
