from domain.entities.place import Place
from infrastructure.models.alchemy.routes import Place as PlaceModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces import PlaceRepository


class SqlAlchemyPlacesRepository(SqlAlchemyModelRepository[Place], PlaceRepository):
    MODEL = PlaceModel
    ENTITY = Place

    def convert_to_model(self, entity: Place) -> PlaceModel:
        return PlaceModel(
            id=entity.id,
            city=entity.city,
            name=entity.name,
            category=entity.category,
            type=entity.type,
            tags=entity.tags,
            coordinates=entity.coordinates,
            photo=entity.photo,
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
            photo=model.photo,
            map_name=model.map_name,
        )
