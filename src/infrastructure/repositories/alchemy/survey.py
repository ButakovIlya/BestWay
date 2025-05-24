from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_, func, select

from domain.entities.survey import Survey
from infrastructure.models.alchemy.surveys import Survey as SurveyModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces.survey import SurveyRepository


class SqlAlchemySurveysRepository(SqlAlchemyModelRepository[Survey], SurveyRepository):
    MODEL = SurveyModel
    ENTITY = Survey
    LIST_DTO: Survey

    async def get_by_user_and_id(self, model_id: int, user_id: int) -> Optional[Survey]:
        """Получить анкету по ID и user_id"""
        stmt = select(self.MODEL).where(and_(self.MODEL.id == model_id, self.MODEL.author_id == user_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            return self.convert_to_entity(model)
        else:
            return None

    async def get_users_surveys_count(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(self.MODEL).where(self.MODEL.author_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def get_list_by_user(self, user_id: int) -> List[Survey]:
        stmt = select(self.MODEL).where(self.MODEL.author_id == user_id)
        result = await self._session.execute(stmt)
        return [self.convert_to_entity(model) for model in result.scalars().all()]

    def convert_to_model(self, entity: Survey) -> SurveyModel:
        return SurveyModel(
            id=entity.id,
            name=entity.name,
            city=entity.city,
            author_id=entity.author_id,
            status=entity.status,
            data=entity.data,
            places=entity.places,
            created_at=entity.created_at or datetime.now(),
            updated_at=entity.updated_at or datetime.now(),
        )

    def convert_to_entity(self, model: SurveyModel) -> Survey:
        return Survey(
            id=model.id,
            name=model.name,
            city=model.city,
            author_id=model.author_id,
            status=model.status,
            data=model.data,
            places=model.places,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
