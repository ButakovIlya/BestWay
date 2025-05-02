from abc import abstractmethod
from typing import Any, List

from infrastructure.repositories.interfaces.base import ModelRepository


class SurveyRepository(ModelRepository):
    @abstractmethod
    async def get_users_surveys_count(self, user_id: int) -> int:
        """Получить колво анкет пользователя"""
        pass

    @abstractmethod
    async def get_list_by_user(self, user_id: int) -> List[Any]:
        """Получить все анкеты пользователя"""
        pass

    @abstractmethod
    async def get_by_user_and_id(self, model_id: int, user_id: int) -> Any:
        """Получить анкету по ID и user_id"""
        pass
