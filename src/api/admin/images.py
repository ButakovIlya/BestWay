from infrastructure.models.alchemy.routes import Place
from infrastructure.orm.base import BaseViewSet

from .schemas import PlaceCreate, PlacePatch, PlacePut, PlaceRead


class PlaceViewSet(BaseViewSet[PlaceCreate, PlacePut, PlacePatch, PlaceRead]):
    model = Place
    schema_read = PlaceRead
    schema_create = PlaceCreate
    schema_put = PlacePut
    schema_patch = PlacePatch
    prefix = "/places"
    tags = ["Places"]
