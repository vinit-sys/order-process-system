from sqlalchemy import Column, String, Float, Enum, ForeignKey, Table, Integer, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.connections.database import db
import enum
from .base import BaseModel


class OrderStatus(str, enum.Enum):
    """Enumeration representing possible statuses of an order."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"


order_items = Table(
    "order_items",
    db.Base.metadata,
    Column("order_id", String(36), ForeignKey("orders.order_id")),
    Column("item_id", String(36), ForeignKey("item.id")),
    Column("quantity", Integer, default=1),
    Column("price_at_time", Float),  # Store price at time of order
)


class Order(BaseModel, db.Base):
    """Model representing an order placed by a user."""

    __tablename__ = "orders"

    id = None
    order_id = Column(String, primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id"), index=True)
    user = relationship("User", backref="orders")
    items = relationship("Item", secondary=order_items, backref="orders")
    total_amount = Column(Float)
    status = Column(String, default=OrderStatus.PENDING)
    completed_at = Column(DateTime, nullable=True)
