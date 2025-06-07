from typing import Any, List

from sqlalchemy import Result, Select, func, select
from sqlalchemy.orm import joinedload, selectinload

from application.use_cases.routes.dto import RouteFeedFiltersDTO
from common.exceptions import APIException
from domain.entities.route import Route
from infrastructure.models.alchemy.routes import Photo, Place
from infrastructure.models.alchemy.routes import Route as RouteModel
from infrastructure.models.alchemy.routes import RoutePlace
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces.route import RouteRepository


class SqlAlchemyRoutesRepository(SqlAlchemyModelRepository[Route], RouteRepository):
    MODEL = RouteModel
    ENTITY = Route

    async def get_by_id(self, model_id: int, **filters: Any) -> Route:
        """Получить маршрут по id и фильтрам"""
        filters_with_id = {"id": model_id, **filters}
        stmt = (
            select(RouteModel)
            .filter_by(**filters_with_id)
            .options(
                joinedload(RouteModel.author),
                joinedload(RouteModel.photos),
                joinedload(RouteModel.places).joinedload(RoutePlace.place).joinedload(Place.photos),
            )
        )
        result = await self._session.execute(stmt)
        model = result.unique().scalar_one_or_none()
        if not model:
            raise APIException(
                code=404, message=f"Объект модели `{self.MODEL.__tablename__}` c id={model_id} не найден"
            )
        return self.convert_to_entity(model)

    async def get_list_models(self, **filters: Any) -> List[Route]:
        """Получить маршруты по фильтрам"""
        stmt = (
            select(RouteModel)
            .filter_by(**filters)
            .options(
                joinedload(RouteModel.author),
                joinedload(RouteModel.photos),
                joinedload(RouteModel.places).joinedload(RoutePlace.place).joinedload(Place.photos),
            )
        )
        return await self._session.execute(stmt)

    async def get_list_by_filters(self, filters: RouteFeedFiltersDTO, add_filters: Any) -> Result:
        """Получить маршруты по фильтрам"""
        stmt = await self._create_stmt_by_filters(filters, add_filters)
        result = await self._session.execute(stmt)
        return result

    async def _create_stmt_by_filters(self, filters: RouteFeedFiltersDTO, add_filters: Any) -> Select:
        MODEL = RouteModel
        stmt = (
            select(MODEL)
            .filter_by(**add_filters)
            .options(
                selectinload(MODEL.places),
                selectinload(MODEL.photos),
            )
        )
        raw_filters = filters.model_dump(exclude_unset=True)

        # OUTER JOIN для фотографий (для has_photos) и обычный JOIN для places
        stmt = (
            stmt.outerjoin(Photo, Photo.route_id == MODEL.id)
            .join(RoutePlace, RoutePlace.route_id == MODEL.id)
            .group_by(MODEL.id)
        )

        # Фильтр по аватарке
        if "has_avatar" in raw_filters:
            if raw_filters["has_avatar"]:
                stmt = stmt.where(MODEL.photo.isnot(None))
            else:
                stmt = stmt.where(MODEL.photo.is_(None))

        # Фильтр по связанным фотографиям (Photo)
        if "has_photos" in raw_filters:
            if raw_filters["has_photos"]:
                stmt = stmt.having(func.count(func.distinct(Photo.id)) > 0)

        # Фильтры по количеству мест (RoutePlace)
        places_count = raw_filters.get("places_count")
        places_gte = raw_filters.get("places_gte")
        places_lte = raw_filters.get("places_lte")

        if places_count is not None:
            stmt = stmt.having(func.count(func.distinct(RoutePlace.place_id)) == places_count)
        if places_gte is not None:
            stmt = stmt.having(func.count(func.distinct(RoutePlace.place_id)) >= places_gte)
        if places_lte is not None:
            stmt = stmt.having(func.count(func.distinct(RoutePlace.place_id)) <= places_lte)

        return stmt

    def convert_to_model(self, entity: Route) -> RouteModel:
        return RouteModel(
            id=entity.id,
            city=entity.city,
            name=entity.name,
            photo=entity.photo,
            author_id=entity.author_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            duration=entity.duration,
            distance=entity.distance,
            json_data=entity.json_data,
        )

    def convert_to_entity(self, model: RouteModel) -> Route:
        return Route(
            id=model.id,
            city=model.city,
            name=model.name,
            photo=model.photo,
            author_id=model.author_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            duration=model.duration,
            distance=model.distance,
            json_data=model.json_data,
            places=[place for place in model.places] if model.places else [],
            photos=[photo for photo in model.photos] if model.photos else [],
        )
