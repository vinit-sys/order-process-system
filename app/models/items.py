from sqlalchemy import Column, String, Float, Boolean
from .base import BaseModel
from app.connections.database import db


class Item(BaseModel, db.Base):
    """
    Represents an item in the system, inheriting common fields from BaseModel.
    """

    __tablename__ = "item"

    name = Column(String(100), nullable=False)
    description = Column(String(500))
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
