from typing import Any

from sqlalchemy import Result, desc, select
from sqlalchemy.orm import joinedload

from common.exceptions import APIException
from domain.entities.post import Post
from infrastructure.models.alchemy.posts import Post as PostModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces.post import PostRepository


class SqlAlchemyPostsRepository(SqlAlchemyModelRepository[Post], PostRepository):
    MODEL = PostModel
    ENTITY = Post

    async def create(self, data: Post) -> Post:
        model = self.convert_to_model(data)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(
            model,
            attribute_names=["author", "route"],
        )
        return self.convert_to_entity(model)

    async def get_by_id(self, model_id: int, **filters: Any) -> Post:
        """Получить пост по id и фильтрам"""
        filters_with_id = {"id": model_id, **filters}
        stmt = (
            select(PostModel)
            .filter_by(**filters_with_id)
            .options(
                joinedload(PostModel.author),
                joinedload(PostModel.route),
            )
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        if not model:
            raise APIException(
                code=404, message=f"Объект модели `{self.MODEL.__tablename__}` c id={model_id} не найден"
            )
        return self.convert_to_entity(model)

    async def get_list_models(self, **filters: Any) -> Result:
        """Получить список постов по фильтрам"""
        stmt = (
            select(PostModel)
            .filter_by(**filters)
            .options(
                joinedload(PostModel.author),
                joinedload(PostModel.route),
            )
            .order_by(desc(PostModel.created_at))
        )
        return await self._session.execute(stmt)

    def convert_to_model(self, entity: Post) -> PostModel:
        return PostModel(
            id=entity.id,
            route_id=entity.route_id,
            author_id=entity.author_id,
            title=entity.title,
            description=entity.description,
            photo=entity.photo,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    def convert_to_entity(self, model: PostModel) -> Post:
        return Post(
            id=model.id,
            route_id=model.route_id,
            author_id=model.author_id,
            title=model.title,
            description=model.description,
            photo=model.photo,
            created_at=model.created_at,
            updated_at=model.updated_at,
            author=model.author if model.author else None,
            route=model.route if model.route else None,
        )
