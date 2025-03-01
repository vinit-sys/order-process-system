from sqlalchemy import Column, String, Boolean
from app.models.base import BaseModel
from app.connections.database import db
import uuid


class User(BaseModel, db.Base):
    """Model representing a user in the system."""

    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
