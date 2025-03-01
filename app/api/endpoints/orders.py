from fastapi import APIRouter, BackgroundTasks, HTTPException
from app import schemas
from app.connections.database import db
from app.models.managers.orders import OrderManager
from app.services.redis_service import redis_service
import json
import uuid

router = APIRouter()

@router.post("/")
async def create_order(
    order: schemas.OrderCreate,
    background_tasks: BackgroundTasks,
):
    """Creates a new order and pushes it to the Redis queue for processing."""
    
    # Generate a unique order ID
    order_id = f"ORD-{uuid.uuid4().hex}"
    order_data = json.dumps({"order_id": order_id})

    async with db.session() as session:
        order_manager = OrderManager(session)
        # Persist order in the database
        new_order = await order_manager.create_order(order_id, order.user_id, order.item_ids, order.total_amount)
    
    # Push the order ID to Redis queue for background processing
    redis_service.redis_conn.rpush("push_order_to_pipeline", order_data)

    return new_order


@router.get("/status")
async def get_queue_status():
    """Fetches the status of the Redis order processing queue."""
    return redis_service.get_queue_status()


@router.get("/{order_id}")
async def get_order_status(order_id: str):
    """Retrieves the status of a specific order using its order ID."""
    try:
        async with db.session() as session:
            order_manager = OrderManager(session)
            order = await order_manager.get_order(order_id)
        
        # If order is not found, return a 404 error
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        return order
    finally:
        # Close the database session after query execution
        db.close()
