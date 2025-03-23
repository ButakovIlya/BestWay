from typing import Optional
from sqlalchemy import select

from domain.entities.user import User
from infrastructure.models.alchemy.users import User as UserModel
from infrastructure.repositories.alchemy.base import SqlAlchemyResourceRepository
from infrastructure.repositories.interfaces import UserRepository


class SqlAlchemyUsersRepository(SqlAlchemyResourceRepository[User], UserRepository):
    MODEL = UserModel
    ENTITY = User

    async def get_by_phone(self, phone: str) -> Optional[UserModel]:
        stmt = select(self.MODEL).where(self.MODEL.phone == phone)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()


    def convert_to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            phone=entity.phone,
            first_name=entity.first_name,
            last_name=entity.last_name,
            middle_name=entity.middle_name,
            registration_date=entity.registration_date,
            is_banned=entity.is_banned,
            is_admin=entity.is_admin,
            photo=entity.photo,
            description=entity.description,
        )

    def convert_to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            phone=model.phone,
            first_name=model.first_name,
            last_name=model.last_name,
            middle_name=model.middle_name,
            registration_date=model.registration_date,
            is_banned=model.is_banned,
            is_admin=model.is_admin,
            photo=model.photo,
            description=model.description,
        )
