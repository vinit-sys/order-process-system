from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
# from ...services.order_service import order_service
# from ...services.redis_service import redis_service
from app.models.order import Order, OrderStatus
from app import schemas
from app.connections.database import db
from app.models.managers.orders import OrderManager
from sqlalchemy.orm import Session
from datetime import datetime
from app.services.redis_service import redis_service
import json
import uuid


router = APIRouter()

@router.post("/")
async def create_order(
    order: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
):
    order_id = f"ORD-{uuid.uuid4().hex}"
    order_data = json.dumps({"order_id": order_id})

    async with db.session() as session:
        order_manager = OrderManager(session)
        new_order = await order_manager.create_order(order_id,order.user_id,order.item_ids,order.total_amount)
    print(f"orfeff:{order_data}")
    redis_service.redis_conn.rpush("push_order_to_pipeline", order_data)
    return new_order


@router.get("/status")
async def get_queue_status():
    return redis_service.get_queue_status()

@router.get("/{order_id}")
async def get_order_status(order_id: str):
    try:
        async with db.session() as session:
            order_manager = OrderManager(session)
            order = await order_manager.get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    finally:
        db.close()
