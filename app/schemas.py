from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus

class OrderCreate(BaseModel):
    user_id: str
    item_ids: List[str]
    total_amount: float

class OrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MetricsResponse(BaseModel):
    total_processed: int
    average_processing_time: float
    status_counts: dict[OrderStatus, int]