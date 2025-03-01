from fastapi import HTTPException
from app.connections.database import db
from app.models.managers.orders import OrderManager
from app.services.redis_service import redis_service

async def push_order_to_db(order, order_id):
    async with db.session() as session:
        order_manager = OrderManager(session)
        new_order = await order_manager.create_order(order_id,order["user_id"],order["item_ids"],order["total_amount"])
    
    queue_position = await redis_service.add_order_to_queue(new_order.order_id)
    if queue_position is None:
        raise HTTPException(status_code=500, detail="Failed to queue order")