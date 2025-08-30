from sqlalchemy import delete, func, select, update

from domain.entities.route_places import RoutePlaces
from infrastructure.models.alchemy.routes import RoutePlace as RoutePlaceModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces.route_places import RoutePlacesRepository


class SqlAlchemyRoutePlacesRepository(SqlAlchemyModelRepository[RoutePlaces], RoutePlacesRepository):
    MODEL = RoutePlaceModel
    ENTITY = RoutePlaces

    async def create(self, data: RoutePlaces) -> RoutePlaces:
        model = self.convert_to_model(data)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(
            model,
            attribute_names=["place"],
        )
        return self.convert_to_entity(model)

    async def update_order(self, route_place_id: int, order: int) -> None:
        """Изменить порядок места маршрута"""
        stmt = update(self.MODEL).where(self.MODEL.id == route_place_id).values(order=order)
        await self._session.execute(stmt)

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

    async def copy(self, route_id: int, places: list[RoutePlaces]) -> list[RoutePlaces]:
        """Скопировать места маршрута в новый маршрут"""
        new_places: list[RoutePlaces] = []
        for place in places:
            new_place = RoutePlaces(
                route_id=route_id,
                place_id=place.place_id,
                order=place.order if hasattr(place, "order") else 1,
            )
            new_places.append(new_place)

        return await self.bulk_create(new_places)

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
            place=model.place if model.place else None,
        )
