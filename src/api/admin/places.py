from infrastructure.models.alchemy.routes import Place
from infrastructure.orm.base import BaseViewSet
from .schemas import PlaceCreate, PlaceRead, PlaceUpdate


class PlaceViewSet(BaseViewSet[PlaceCreate, PlaceUpdate, PlaceRead]):
    model = Place
    schema_read = PlaceRead
    schema_create = PlaceCreate
    schema_update = PlaceUpdate
    prefix = "/places"
    tags = ["Places"]
