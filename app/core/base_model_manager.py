from typing import TypeVar, Type, Optional, List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from app.db.database import db
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType")

class DefaultModelManager:
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, data: Dict[str, Any]) -> Optional[ModelType]:
        """Create a new record"""
        try:
            async with db.session() as session:
                # Add timestamps
                data['created_at'] = datetime.utcnow()
                data['updated_at'] = datetime.utcnow()
                
                instance = self.model(**data)
                session.add(instance)
                await session.commit()
                await session.refresh(instance)
                return instance
        except SQLAlchemyError as e:
            logger.error(f"Error creating {self.model.__name__}: {e}")
            return None

    async def update(self, id: Any, data: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record by id"""
        try:
            async with db.session() as session:
                data['updated_at'] = datetime.utcnow()
                
                stmt = (
                    update(self.model)
                    .where(self.model.id == id)
                    .values(**data)
                    .returning(self.model)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            return None

    async def delete(self, id: Any) -> bool:
        """Delete a record by id"""
        try:
            async with db.session() as session:
                stmt = (
                    delete(self.model)
                    .where(self.model.id == id)
                    .returning(self.model.id)
                )
                result = await session.execute(stmt)
                await session.commit()
                return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            return False

    async def get(self, id: Any) -> Optional[ModelType]:
        """Get a record by id"""
        try:
            async with db.session() as session:
                stmt = select(self.model).where(self.model.id == id)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching {self.model.__name__} {id}: {e}")
            return None

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering"""
        try:
            async with db.session() as session:
                stmt = select(self.model)

                # Apply filters if provided
                if filters:
                    for field, value in filters.items():
                        if hasattr(self.model, field):
                            stmt = stmt.where(getattr(self.model, field) == value)

                stmt = stmt.offset(skip).limit(limit)
                result = await session.execute(stmt)
                return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching multiple {self.model.__name__}: {e}")
            return []

    async def exists(self, **kwargs) -> bool:
        """Check if a record exists with given criteria"""
        try:
            async with db.session() as session:
                stmt = select(self.model)
                for field, value in kwargs.items():
                    if hasattr(self.model, field):
                        stmt = stmt.where(getattr(self.model, field) == value)
                result = await session.execute(stmt)
                return result.scalar_one_or_none() is not None
        except SQLAlchemyError as e:
            logger.error(f"Error checking existence of {self.model.__name__}: {e}")
            return False