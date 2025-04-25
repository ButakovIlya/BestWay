from domain.entities.route_places import RoutePlaces
from infrastructure.models.alchemy.routes import RoutePlace as RoutePlaceModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces.route_places import RoutePlacesRepository


class SqlAlchemyRoutePlacesRepository(SqlAlchemyModelRepository[RoutePlaces], RoutePlacesRepository):
    MODEL = RoutePlaceModel
    ENTITY = RoutePlaces

    def convert_to_model(self, entity: RoutePlaces) -> RoutePlaceModel:
        return RoutePlaceModel(
            id=entity.id,
            route_id=entity.route_id,
            place_id=entity.place_id,
            order=entity.order,
        )

    def convert_to_entity(self, model: RoutePlaceModel) -> RoutePlaces:
        return RoutePlaces(
            id=model.id,
            route_id=model.route_id,
            place_id=model.place_id,
            order=model.order,
        )
