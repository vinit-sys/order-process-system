from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import logging
from app.core.config import settings
import os
import traceback

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self._engine = None
        self._async_session_factory = None
        self.Base = declarative_base()

    def init_db(self):
        """Initialize database connection"""
        if not self._engine:
            try:
                # Ensure the database directory exists
                db_dir = os.path.dirname(settings.DB_PATH)
                print(db_dir)


                os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)
                
                # SQLite async URL format
                DATABASE_URL = f"sqlite+aiosqlite:///{settings.DB_PATH}"

                self._engine = create_async_engine(
                    DATABASE_URL,
                    echo=settings.DB_ECHO_LOG,
                    # SQLite specific: enable foreign key constraints
                    connect_args={"check_same_thread": False,"timeout":30}
                )

                self._async_session_factory = sessionmaker(
                    self._engine,
                    class_=AsyncSession,
                    expire_on_commit=False,
                    autocommit=False,
                    autoflush=False
                )
                
                logger.info("Database connection initialized successfully")
            except Exception as e:
                traceback.print_exc()
                logger.error(f"Failed to initialize database connection: {str(e)}")
                raise

    async def create_all(self):
        """Create all tables"""
        if not self._engine:
            self.init_db()
        async with self._engine.begin() as conn:
            await conn.run_sync(self.Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session"""
        if not self._async_session_factory:
            self.init_db()

        session: AsyncSession = self._async_session_factory()
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self):
        """Close database connection"""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._async_session_factory = None
            logger.info("Database connection closed")

# Global database instance
db = Database()