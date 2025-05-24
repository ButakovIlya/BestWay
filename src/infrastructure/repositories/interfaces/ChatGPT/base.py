from abc import ABC, abstractmethod

from application.use_cases.routes.enums import RouteGenerationMode as Mode
from infrastructure.managers.ChatGPT.dto import ChatGPTContentData


class ClassificationManager(ABC):
    @abstractmethod
    def generate_route(self, route_data: ChatGPTContentData, mode: Mode = Mode.FULL) -> dict:
        pass
