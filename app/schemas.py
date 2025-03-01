from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.order import OrderStatus

class OrderCreate(BaseModel):
    user_id: str
    item_ids: List[str]
    total_amount: float
