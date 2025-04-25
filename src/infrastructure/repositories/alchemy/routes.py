from domain.entities.route import Route
from infrastructure.models.alchemy.routes import Route as RouteModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces.route import RouteRepository


class SqlAlchemyRoutesRepository(SqlAlchemyModelRepository[Route], RouteRepository):
    MODEL = RouteModel
    ENTITY = Route

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
            json=entity.json,
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
            json_data=model.json,
            # place_ids=[place.place_id for place in model.places] if model.places else [],
            # photo_ids=[photo.id for photo in model.photos] if model.photos else [],
            # like_ids=[like.id for like in model.likes] if model.likes else [],
            # comment_ids=[comment.id for comment in model.comments] if model.comments else [],
        )
