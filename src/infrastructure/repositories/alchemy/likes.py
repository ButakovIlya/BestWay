from typing import List

from sqlalchemy import and_, select

from application.use_cases.likes.dto import LikeDTO
from domain.entities.like import Like
from infrastructure.models.alchemy.routes import Like as LikeModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces import LikeRepository


class SqlAlchemyLikesRepository(SqlAlchemyModelRepository[Like], LikeRepository):
    MODEL = LikeModel
    ENTITY = Like
    LIST_DTO = LikeDTO

    async def get_list_by_route_id(self, route_id: int) -> List[Like]:
        result = await self._session.execute(select(LikeModel).where(LikeModel.route_id == route_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

    async def get_list_by_place_id(self, place_id: int) -> List[Like]:
        result = await self._session.execute(select(LikeModel).where(LikeModel.place_id == place_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

    async def get_list_by_user_id(self, user_id: int) -> List[Like]:
        result = await self._session.execute(select(LikeModel).where(LikeModel.author_id == user_id))
        return [self.convert_to_entity(row) for row in result.scalars().all()]

    async def check_if_user_has_like(self, data: LikeDTO) -> bool:
        stmt = select(LikeModel).where(
            and_(
                LikeModel.route_id == data.route_id,
                LikeModel.place_id == data.place_id,
                LikeModel.post_id == data.post_id,
                LikeModel.author_id == data.author_id,
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def convert_to_model(self, entity: Like) -> LikeModel:
        return LikeModel(
            id=entity.id,
            author_id=entity.author_id,
            route_id=entity.route_id,
            post_id=entity.post_id,
            place_id=entity.place_id,
            timestamp=entity.timestamp,
        )

    def convert_to_entity(self, model: LikeModel) -> Like:
        return Like(
            id=model.id,
            author_id=model.author_id,
            route_id=model.route_id,
            place_id=model.place_id,
            post_id=model.post_id,
            timestamp=model.timestamp,
        )
