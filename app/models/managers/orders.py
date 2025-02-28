from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from ..items import Item
from ..user import User
from ..order import Order, OrderStatus, order_items

class OrderManager:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(self, order_id: str, user_id: str, items: list, total_amount: float) -> Order:
        try:
            total_amount_org = 0
            valid_items = []
            user = await self.session.get(User, user_id)

            if not user:
                raise ValueError(f"Invalid user ID: {user_id}")

            for item_id in items:
                item = await self.session.get(Item, item_id)
                if item:
                    price_at_time = item.price
                    total_amount_org += price_at_time
                    valid_items.append({"item_id": item_id,"quantity":1, "price_at_time": price_at_time})
                else:
                    raise ValueError(f"Invalid item ID: {item_id}")
            
            if round(total_amount,1) != round(total_amount_org,1):
                raise ValueError(f"Invalid  total_amount: org:{total_amount_org} your:{total_amount}")

            new_order = Order(order_id=order_id, user_id=user_id, total_amount=total_amount_org, status=OrderStatus.PENDING)
            self.session.add(new_order)
            await self.session.commit()
            await self.session.refresh(new_order)

            for item_data in valid_items:
                await self.session.execute(order_items.insert().values(order_id=new_order.order_id, **item_data))
            await self.session.commit()
            return new_order
        except (SQLAlchemyError, ValueError) as e:
            await self.session.rollback()
            raise e

    async def get_order(self, order_id: str) -> Order:
        return await self.session.get(Order, order_id)

    async def update_order(self, order_id: str, **kwargs) -> Order:
        try:
            order = await self.session.get(Order, order_id)
            if order:
                for key, value in kwargs.items():
                    if hasattr(order, key):
                        setattr(order, key, value)
                await self.session.commit()
                await self.session.refresh(order)
            return order
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e
        
    async def update_bulk_orders(self, order_ids: list, **kwargs) -> Order:
        try:
            orders_result = await self.session.execute(
                select(Order).where(Order.order_id.in_(order_ids))
            )
            orders = orders_result.scalars().all()
            if orders:
                for order in orders:
                    for key, value in kwargs.items():
                        if hasattr(order, key):
                            setattr(order, key, value)
                await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def delete_order(self, order_id: str) -> bool:
        try:
            order = await self.session.get(Order, order_id)
            if order:
                await self.session.delete(order)
                await self.session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            await self.session.rollback()
            raise e

    async def get_all_orders(self, status: str = None):
        query = select(Order)
        if status:
            query = query.where(Order.status == status)
        result = await self.session.execute(query)
        return result.scalars().all()
