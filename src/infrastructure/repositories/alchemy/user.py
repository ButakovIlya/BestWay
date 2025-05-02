from typing import List, Optional

from sqlalchemy import delete, exists, select

from domain.entities.user import User
from infrastructure.models.alchemy.users import User as UserModel
from infrastructure.repositories.alchemy.base import SqlAlchemyModelRepository
from infrastructure.repositories.interfaces import UserRepository


class SqlAlchemyUsersRepository(SqlAlchemyModelRepository[User], UserRepository):
    MODEL = UserModel
    ENTITY = User

    async def get_by_phone(self, phone: str) -> Optional[User]:
        stmt = select(self.MODEL).where(self.MODEL.phone == phone)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            return self.convert_to_entity(model)
        else:
            return None

    async def get_list(self) -> List[User]:
        stmt = select(self.MODEL)
        return await self._session.execute(stmt)

    async def exists_by_phone(self, phone: str) -> bool:
        stmt = select(exists().where(self.MODEL.phone == phone))
        result = await self._session.execute(stmt)
        return bool(result.scalar())

    async def delete_by_phone(self, phone: str) -> bool:
        stmt = delete(self.MODEL).where(self.MODEL.phone == phone)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0

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
            gender=entity.gender,
            birth_date=entity.birth_date,
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
            gender=model.gender,
            birth_date=model.birth_date,
        )
