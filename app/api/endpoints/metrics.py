from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select
from app.connections.database import db
from app.models.order import Order, OrderStatus
from app.services.redis_service import redis_service

router = APIRouter()

@router.get("/")
async def get_order_metrics():
    """Fetch key metrics for orders."""
    try:
        # Fetch average processing time
        async with db.session() as session:
            avg_time_query = select(func.avg(Order.completed_at - Order.created_at)).where(Order.status == OrderStatus.COMPLETED)
            avg_time_result = await session.execute(avg_time_query)
            avg_processing_time = avg_time_result.scalar()
            avg_processing_time = avg_processing_time.total_seconds() if avg_processing_time else 0

            # Fetch order counts per status
            status_query = select(Order.status, func.count()).group_by(Order.status)
            status_result = await session.execute(status_query)
            status_counts = dict(status_result.all())

        # Ensure all statuses are present
        order_statuses = {status.value: status_counts.get(status, 0) for status in OrderStatus}

        return {
            "average_processing_time_seconds": avg_processing_time,
            "order_status_counts": order_statuses
        }
    except Exception as e:
        return {"error": f"Failed to fetch metrics: {str(e)}"}
