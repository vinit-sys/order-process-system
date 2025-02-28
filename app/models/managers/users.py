from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from ..user import User

class UserManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, name: str, email: str, is_active: bool = True, id: str = None) -> User:
        try:
            if id:
                new_user = User(id=id,name=name, email=email, is_active=is_active)
            else:
                new_user = User(name=name, email=email, is_active=is_active)
            self.session.add(new_user)
            await self.session.commit()
            await self.session.refresh(new_user)
            return new_user
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_user(self, user_id: int) -> User:
        return await self.session.get(User, user_id)

    async def update_user(self, user_id: int, **kwargs) -> User:
        try:
            user = await self.session.get(User, user_id)
            if user:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                await self.session.commit()
                await self.session.refresh(user)
            return user
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def bulk_update_users(self, user_ids: list, **kwargs):
        try:
            users = await self.session.execute(
                User.__table__.select().where(User.id.in_(user_ids))
            )
            users = users.scalars().all()
            for user in users:
                for key, value in kwargs.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete_user(self, user_id: int) -> bool:
        try:
            user = await self.session.get(User, user_id)
            if user:
                await self.session.delete(user)
                await self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def bulk_delete_users(self, user_ids: list) -> bool:
        try:
            users = await self.session.execute(
                User.__table__.select().where(User.id.in_(user_ids))
            )
            users = users.scalars().all()
            if users:
                for user in users:
                    await self.session.delete(user)
                await self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_all_users(self, is_active: bool = None):
        query = User.__table__.select()
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        result = await self.session.execute(query)
        return result.scalars().all()
