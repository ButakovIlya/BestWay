import logging
from typing import List

from pydantic import ValidationError

from application.use_cases.base import UseCase
from application.use_cases.routes.enums import RouteGenerationMode as Mode
from common.exceptions import APIException
from domain.entities.place import Place
from domain.entities.route import Route
from domain.entities.route_places import RoutePlaces
from domain.entities.survey import Survey
from domain.entities.user import User
from infrastructure.managers.ChatGPT.dto import (
    ChatGPTContentData,
    ChatGPTPlaceData,
    ChatGPTRouteData,
    ChatGPTSurveyData,
    ChatGPTUserData,
)
from infrastructure.repositories.interfaces.ChatGPT.base import ClassificationManager
from infrastructure.uow import UnitOfWork

logger = logging.getLogger(__name__)


class ChatGPTRouteGenerateUseCase(UseCase):
    def __init__(
        self,
        uow: UnitOfWork,
        route_generate_gpt_manager: ClassificationManager,
    ) -> None:
        self._uow = uow
        self._route_generate_gpt_manager = route_generate_gpt_manager

    async def execute(self, user_id: int, survey_id: int, mode: str = Mode.FULL.name) -> Route:
        logger.info(
            f"Start route gpt generate use case for user: {user_id} with survey: {survey_id} in {mode} mode"
        )
        data = await self._create_content(user_id, survey_id)
        logger.info(f"Content data: {data}")
        # route_data = self._route_generate_gpt_manager.generate_route(data, Mode(mode))
        route_data = {
            "name": "Маршрут по Пермскому театру, ресторану и цирку",
            "type": "На машине",
            "places": [89, 92, 93],
        }
        validated_route_data = await self._validate_generated_route(route_data, user_id)
        print(f"validated_route_data: {validated_route_data}")
        route = await self._create_route(validated_route_data, survey_id)
        logger.info("End route chatgpt generate use case")
        return route

    async def _create_content(self, user_id: int, survey_id: int) -> ChatGPTContentData:
        async with self._uow(autocommit=True):
            user: User = await self._uow.users.get_by_id(user_id)
            survey: Survey = await self._uow.surveys.get_by_id(survey_id)
            places: List[Place] = await self._uow.places.get_list()

            user_dto = ChatGPTUserData(
                first_name=user.first_name,
                last_name=user.last_name,
                middle_name=user.middle_name,
                description=user.description,
                gender=user.gender,
                birth_date=user.birth_date,
            )

            survey_dto = ChatGPTSurveyData(city=survey.city, data=survey.data, places=survey.places)

            places_dto = [
                ChatGPTPlaceData(
                    id=place.id,
                    name=place.name,
                    category=place.category,
                    type=place.type,
                    tags=place.tags,
                    coordinates=place.coordinates,
                    map_name=place.map_name,
                )
                for place in places
            ]

            return ChatGPTContentData(
                user_data=user_dto,
                survey_data=survey_dto,
                places_data=places_dto,
            )

    async def _validate_generated_route(self, route_data: dict, author_id: int) -> ChatGPTRouteData:
        try:
            return ChatGPTRouteData(**route_data, author_id=author_id)
        except ValidationError as e:
            logger.warning(f"ChatGPT responded with invalid route_data: {route_data}. Errors: {e}")
            raise APIException(
                code=400, message=(f"ChatGPT responded with invalid route_data: {route_data}. Errors: {e}")
            )

    async def _create_route(self, validated_route_data: ChatGPTRouteData, survey_id: int) -> Route:
        async with self._uow(autocommit=True):
            survey: Survey = await self._uow.surveys.get_by_id(survey_id)
            route: Route = await self._uow.routes.create(
                Route(**validated_route_data.model_dump(), city=survey.city)
            )
            route_places: List[RoutePlaces] = await self._uow.route_places.bulk_create(
                RoutePlaces(route_id=route.id, place_id=place_id, order=index)
                for index, place_id in enumerate(validated_route_data.places, start=1)
            )
            logger.info(f"Created route: {route}")
            logger.info(f"Created route_places: {route_places}")

            return route
