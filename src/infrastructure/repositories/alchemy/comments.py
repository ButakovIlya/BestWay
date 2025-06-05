from typing import List

from sqlalchemy import select

from application.use_cases.likes.dto import CommentDTO
from domain.entities.comment import Comment
from infrastructure.models.alchemy.routes import Comment as CommentModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces import CommentRepository


class SqlAlchemyCommentsRepository(SqlAlchemyModelRepository[Comment], CommentRepository):
    MODEL = CommentModel
    ENTITY = Comment
    LIST_DTO = CommentDTO

    async def get_list_by_route_id(self, route_id: int) -> List[Comment]:
        result = await self._session.execute(select(CommentModel).where(CommentModel.route_id == route_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

    async def get_list_by_place_id(self, place_id: int) -> List[Comment]:
        result = await self._session.execute(select(CommentModel).where(CommentModel.place_id == place_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

    async def get_list_by_user_id(self, user_id: int) -> List[Comment]:
        result = await self._session.execute(select(CommentModel).where(CommentModel.author_id == user_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

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
            route_id=model.route_id,
            place_id=model.place_id,
            timestamp=model.timestamp,
            comment=model.comment,
        )
