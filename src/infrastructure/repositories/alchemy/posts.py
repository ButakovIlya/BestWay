from typing import Any

from sqlalchemy import Result, Select, desc, func, select
from sqlalchemy.orm import joinedload, selectinload

from common.dto import PostsFiltersDTO
from common.exceptions import APIException
from domain.entities.post import Post
from infrastructure.models.alchemy.posts import Post as PostModel
from infrastructure.models.alchemy.routes import Photo, Place, Route, RoutePlace
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
                joinedload(PostModel.route)
                .selectinload(Route.places)
                .joinedload(RoutePlace.place)
                .selectinload(Place.photos),
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

    async def get_list_by_filters(self, filters: PostsFiltersDTO) -> Result:
        """Получить маршруты по фильтрам"""
        stmt = await self._create_stmt_by_filters(filters)
        result = await self._session.execute(stmt)
        return result

    async def _create_stmt_by_filters(self, filters: PostsFiltersDTO) -> Select:
        MODEL = PostModel
        ROUTE = Route

        stmt = (
            select(MODEL)
            .join(ROUTE, ROUTE.id == MODEL.route_id)
            .outerjoin(Photo, Photo.route_id == ROUTE.id)
            .options(
                joinedload(MODEL.author),
                joinedload(MODEL.route)
                .joinedload(ROUTE.places)
                .joinedload(RoutePlace.place)
                .joinedload(Place.photos),
            )
            .group_by(MODEL.id, ROUTE.id)
            .order_by(MODEL.created_at.desc())
        )

        raw_filters = filters.model_dump(exclude_unset=True)

        # --- фильтры по посту ---
        if title := raw_filters.get("title"):
            stmt = stmt.where(MODEL.title.ilike(f"%{title}%"))

        if desc := raw_filters.get("description"):
            stmt = stmt.where(MODEL.description.ilike(f"%{desc}%"))

        # --- фильтры по маршруту ---
        if route_name := raw_filters.get("route_name"):
            stmt = stmt.where(ROUTE.name.ilike(f"%{route_name}%"))

        if city := raw_filters.get("city"):
            stmt = stmt.where(ROUTE.city == city)

        if rtype := raw_filters.get("type"):
            stmt = stmt.where(ROUTE.type == rtype)

        if (is_custom := raw_filters.get("is_custom")) is not None:
            stmt = stmt.where(ROUTE.is_custom == is_custom)

        # аватарка маршрута
        if (has_avatar := raw_filters.get("has_avatar")) is not None:
            stmt = stmt.where(ROUTE.photo.isnot(None) if has_avatar else ROUTE.photo.is_(None))

        # наличие связанных фото маршрута
        if raw_filters.get("has_photos"):
            stmt = stmt.having(func.count(func.distinct(Photo.id)) > 0)

        # фильтры по количеству мест маршрута
        place_count_expr = func.count(func.distinct(RoutePlace.place_id))
        if (val := raw_filters.get("places_count")) is not None:
            stmt = stmt.having(place_count_expr == val)
        if (val := raw_filters.get("places_gte")) is not None:
            stmt = stmt.having(place_count_expr >= val)
        if (val := raw_filters.get("places_lte")) is not None:
            stmt = stmt.having(place_count_expr <= val)

        return stmt

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
