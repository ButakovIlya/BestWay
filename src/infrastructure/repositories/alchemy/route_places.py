from sqlalchemy import delete, func, select

from domain.entities.route_places import RoutePlaces
from infrastructure.models.alchemy.routes import RoutePlace as RoutePlaceModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces.route_places import RoutePlacesRepository


class SqlAlchemyRoutePlacesRepository(SqlAlchemyModelRepository[RoutePlaces], RoutePlacesRepository):
    MODEL = RoutePlaceModel
    ENTITY = RoutePlaces

    async def get_last_order_by_route_id(self, route_id: int) -> int:
        stmt = select(func.max(RoutePlaceModel.order)).where(RoutePlaceModel.route_id == route_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() or 0

    async def remove_route_place_by_id(self, route_id: int, route_place_id: int | None) -> bool:
        stmt = delete(RoutePlaceModel).where(RoutePlaceModel.route_id == route_id)

        if route_place_id is not None:
            stmt = stmt.where(RoutePlaceModel.id == route_place_id)

        result = await self._session.execute(stmt)
        return bool(result.rowcount)

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
