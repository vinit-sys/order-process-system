from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from ..items import Item

class ItemManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_item(self, name: str, description: str, price: float, is_active: bool = True, id: str = None) -> Item:
        try:
            if id:
                new_item = Item(id=id,name=name, description=description, price=price, is_active=is_active)
            else:
                new_item = Item(name=name, description=description, price=price, is_active=is_active)
            self.session.add(new_item)
            await self.session.commit()
            await self.session.refresh(new_item)
            return new_item
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_item(self, item_id: int) -> Item:
        return await self.session.get(Item, item_id)

    async def update_item(self, item_id: int, **kwargs) -> Item:
        try:
            item = await self.session.get(Item, item_id)
            if item:
                for key, value in kwargs.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
                await self.session.commit()
                await self.session.refresh(item)
            return item
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def bulk_update_items(self, item_ids: list, **kwargs):
        try:
            items = await self.session.execute(
                Item.__table__.select().where(Item.id.in_(item_ids))
            )
            items = items.scalars().all()
            for item in items:
                for key, value in kwargs.items():
                    if hasattr(item, key):
                        setattr(item, key, value)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete_item(self, item_id: int) -> bool:
        try:
            item = await self.session.get(Item, item_id)
            if item:
                await self.session.delete(item)
                await self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def bulk_delete_items(self, item_ids: list) -> bool:
        try:
            items = await self.session.execute(
                Item.__table__.select().where(Item.id.in_(item_ids))
            )
            items = items.scalars().all()
            if items:
                for item in items:
                    await self.session.delete(item)
                await self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_all_items(self, is_active: bool = None):
        query = Item.__table__.select()
        if is_active is not None:
            query = query.where(Item.is_active == is_active)
        result = await self.session.execute(query)
        return result.scalars().all()