from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
# from ...services.order_service import order_service
# from ...services.redis_service import redis_service
from app.models.order import Order, OrderStatus
from app import schemas
from app.connections.database import db
from app.models.managers.orders import OrderManager
from sqlalchemy.orm import Session
from datetime import datetime
from app.tasks.push_order_to_db import push_order_to_db
from app.services.redis_service import redis_service
import json


router = APIRouter()

@router.post("/")
async def create_order(
    order: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
):
    order_id=f"ORD-{int(datetime.now().timestamp()*1000)}"
    order_data = json.dumps({"order_id": order_id, **order.dict()})
    redis_service.redis_conn.rpush("test_check", order_data)
    return {"order_id":order_id}


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
