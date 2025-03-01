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
        """Initialize the Database class with placeholders for engine, session factory, and Base model."""
        self._engine = None
        self._async_session_factory = None
        self.Base = declarative_base()

    def init_db(self):
        """Initialize the database connection and session factory."""
        if not self._engine:
            try:
                # Ensure the database directory exists
                db_dir = os.path.dirname(settings.DB_PATH)
                print(db_dir)

                os.makedirs(os.path.dirname(settings.DB_PATH), exist_ok=True)

                # Define the SQLite async database URL
                DATABASE_URL = f"sqlite+aiosqlite:///{settings.DB_PATH}"

                # Create an async engine for handling database operations
                self._engine = create_async_engine(
                    DATABASE_URL,
                    echo=settings.DB_ECHO_LOG,  # Enable SQL query logging if configured
                    connect_args={
                        "check_same_thread": False,
                        "timeout": 30,
                    },  # SQLite-specific settings
                )

                # Create a session factory for generating async sessions
                self._async_session_factory = sessionmaker(
                    self._engine,
                    class_=AsyncSession,
                    expire_on_commit=False,  # Ensure objects remain usable after commit
                    autocommit=False,
                    autoflush=False,
                )

                logger.info("Database connection initialized successfully")
            except Exception as e:
                traceback.print_exc()
                logger.error(f"Failed to initialize database connection: {str(e)}")
                raise

    async def create_all(self):
        """Create all database tables based on defined models."""
        if not self._engine:
            self.init_db()
        async with self._engine.begin() as conn:
            await conn.run_sync(
                self.Base.metadata.create_all
            )  # Run table creation synchronously

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide an async session for database operations."""
        if not self._async_session_factory:
            self.init_db()

        session: AsyncSession = self._async_session_factory()
        try:
            yield session  # Yield session for usage within the context
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()  # Rollback transaction on error
            raise
        finally:
            await session.close()  # Ensure session is closed after usage

    async def close(self):
        """Close the database connection and clean up resources."""
        if self._engine:
            await self._engine.dispose()  # Dispose the database engine
            self._engine = None
            self._async_session_factory = None
            logger.info("Database connection closed")


# Global database instance
db = Database()
