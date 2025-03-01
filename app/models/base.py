from sqlalchemy import Column, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
import uuid


class BaseModel:
    """
    Base model class that provides common fields for all database models.
    """

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
