from fastapi import HTTPException
from app.connections.database import db
from app.models.managers.orders import OrderManager
from app.services.redis_service import redis_service

async def push_order_to_pipeline(order_id):
    queue_position = await redis_service.add_order_to_queue(order_id)
    if queue_position is None:
        raise HTTPException(status_code=500, detail="Failed to queue order")