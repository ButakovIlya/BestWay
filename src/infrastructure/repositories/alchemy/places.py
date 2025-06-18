from typing import List

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from application.use_cases.places.dto import PlaceDTO
from domain.entities.place import Place
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
