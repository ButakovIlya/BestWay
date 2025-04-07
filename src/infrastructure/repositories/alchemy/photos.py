from domain.entities.photo import Photo
from infrastructure.models.alchemy.routes import Photo as PhotoModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces import PhotoRepository


class SqlAlchemyPhotosRepository(SqlAlchemyModelRepository[Photo], PhotoRepository):
    MODEL = PhotoModel
    ENTITY = Photo

    def convert_to_model(self, entity: Photo) -> PhotoModel:
        return PhotoModel(
            id=entity.id,
            url=entity.url,
            uploaded_at=entity.uploaded_at,
            uploaded_by=entity.uploaded_by,
            place_id=entity.place_id,
            route_id=entity.route_id,
        )

    def convert_to_entity(self, model: PhotoModel) -> Photo:
        return Photo(
            id=model.id,
            url=model.url,
            uploaded_at=model.uploaded_at,
            uploaded_by=model.uploaded_by,
            place_id=model.place_id,
            route_id=model.route_id,
        )
