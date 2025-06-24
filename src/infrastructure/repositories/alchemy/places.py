from typing import List

from sqlalchemy import Result, func, select
from sqlalchemy.orm import selectinload

from application.use_cases.places.dto import PlaceDTO
from common.dto import PlacesFiltersDTO
from domain.entities.place import Place
from infrastructure.models.alchemy.routes import Photo
from infrastructure.models.alchemy.routes import Place as PlaceModel
from infrastructure.models.alchemy.routes import Route, RoutePlace
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces import PlaceRepository


class SqlAlchemyPlacesRepository(SqlAlchemyModelRepository[Place], PlaceRepository):
    MODEL = PlaceModel
    ENTITY = Place
    LIST_DTO = PlaceDTO

    async def get_list_by_route_id(self, route_id: int) -> List[Place]:
        """Получить места, связанные с маршрутом через RoutePlace"""
        result = await self._session.execute(
            select(Route)
            .options(selectinload(Route.places).selectinload(RoutePlace.place))
            .where(Route.id == route_id)
        )
        route = result.scalar_one_or_none()
        if not route or not route.places:
            return []

        place_models = [rp.place for rp in route.places if rp.place]
        return [self.convert_to_entity(place_model) for place_model in place_models]

    async def get_list_by_filters(self, filters: PlacesFiltersDTO) -> Result:
        stmt = self._create_stmt_by_filters(filters)
        result = await self._session.execute(stmt)
        return result

    def _create_stmt_by_filters(self, filters: PlacesFiltersDTO) -> List[Place]:
        """Получить места по фильтрам"""
        filters = filters.model_dump(exclude_unset=True)
        MODEL = PlaceModel
        stmt = select(MODEL).options(selectinload(MODEL.photos))

        # Простой фильтр по полям с оператором ==
        simple_eq_fields = {
            "city": MODEL.city,
        }
        for field_name, model_field in simple_eq_fields.items():
            value = filters.get(field_name)
            if value is not None:
                stmt = stmt.where(model_field == value)

        # Фильтр по категориям: category IN (...)
        if filters.get("categories"):
            stmt = stmt.where(MODEL.category.in_(filters.get("categories")))

        # Фильтр по типам: type IN (...)
        if filters.get("types"):
            stmt = stmt.where(MODEL.type.in_(filters.get("types")))

        # Фильтр по имени с ilike
        name = filters.get("name")
        if name:
            stmt = stmt.where(MODEL.name.ilike(f"%{name}%"))

        # Фильтр по аватарке
        has_avatar = filters.get("has_avatar")
        if has_avatar is not None:
            stmt = stmt.where(MODEL.photo.isnot(None) if has_avatar else MODEL.photo.is_(None))

        # Фильтр по наличию связанных фото
        if filters.get("has_photos"):
            stmt = (
                stmt.join(Photo, PlaceModel.photos)
                .group_by(PlaceModel.id)
                .having(func.count(func.distinct(Photo.id)) > 0)
            )
        return stmt

    def convert_to_model(self, entity: Place) -> PlaceModel:
        return PlaceModel(
            id=entity.id,
            city=entity.city,
            name=entity.name,
            category=entity.category,
            object_id=entity.object_id,
            type=entity.type,
            tags=entity.tags,
            coordinates=entity.coordinates,
            photo=entity.photo,
            photos=entity.photos or [],
            map_name=entity.map_name,
        )

    def convert_to_entity(self, model: PlaceModel) -> Place:
        return Place(
            id=model.id,
            city=model.city,
            name=model.name,
            category=model.category,
            type=model.type,
            tags=model.tags,
            coordinates=model.coordinates,
            object_id=model.object_id,
            photo=model.photo,
            photos=model.photos,
            map_name=model.map_name,
        )
