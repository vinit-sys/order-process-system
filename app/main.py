from fastapi import FastAPI, Request
from .api.endpoints import orders
from .api.endpoints import metrics

from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

# from .tasks.workers import start_workers
from .core.logging import logger
from app.connections.database import db
from app.core.workers.worker_manager import worker_manager
from app.core.workers.order_processor import OrderProcessor, RedisOrderProcessor
from app.core.config import settings
from app.services.redis_service import redis_service
import traceback

app = FastAPI()


@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    """
    Middleware to handle exceptions globally and return appropriate error responses.
    """
    try:
        response = await call_next(request)
        return response
    except SQLAlchemyError as e:
        traceback.print_exc()  # Log the full traceback for debugging
        return JSONResponse(
            status_code=500,
            content={"error": "Database Error", "detail": str(e)},
        )
    except Exception as e:
        traceback.print_exc()  # Log the full traceback for debugging
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(e)},
        )


# Include routers for handling different API endpoints
app.include_router(orders.router, prefix="/orders", tags=["orders"])
app.include_router(metrics.router, prefix="/metrics", tags=["metrics"])


@app.on_event("startup")
async def startup():
    """
    Startup event handler to initialize the database, flush Redis, and start workers.
    """
    db.init_db()
    redis_service.redis_conn.flushall()  # Clear all Redis data on startup
    await db.create_all()  # Create database tables if they do not exist

    # Initialize and start worker processes
    order_processor = OrderProcessor(num_processes=settings.WORKER_PROCESSES)
    redis_order = RedisOrderProcessor(num_processes=settings.WORKER_PROCESSES)
    worker_manager.add_worker(order_processor)
    worker_manager.add_worker(redis_order)
    worker_manager.start_all()


@app.on_event("shutdown")
async def shutdown():
    """
    Shutdown event handler to properly close the database connection and stop workers.
    """
    await db.close()
    worker_manager.stop_all()
