from fastapi import FastAPI, Request
from .api.endpoints import orders
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
# from .tasks.workers import start_workers
from .core.logging import logger
from app.connections.database import db
from app.core.workers.worker_manager import worker_manager
from app.core.workers.order_processor import OrderProcessor, RedisOrderProcessor
from app.core.config import settings
import traceback

app = FastAPI()

@app.middleware("http")
async def exception_middleware(request: Request, call_next):
    try:
        response = await call_next(request)  # Process request
        return response
    except SQLAlchemyError as e:
        traceback.print_exc()  # Log error for debugging
        return JSONResponse(
            status_code=500,
            content={"error": "Database Error", "detail": str(e)},
        )
    except Exception as e:
        traceback.print_exc()  # Log error for debugging
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "detail": str(e)},
        )

# Include routers
app.include_router(orders.router, prefix="/orders", tags=["orders"])


@app.on_event("startup")
async def startup():
    db.init_db()
    await db.create_all()
    order_processor = OrderProcessor(num_processes=settings.WORKER_PROCESSES)
    redis_order = RedisOrderProcessor(num_processes=settings.WORKER_PROCESSES)
    worker_manager.add_worker(order_processor)
    worker_manager.add_worker(redis_order)
    worker_manager.start_all()

@app.on_event("shutdown")
async def shutdown():
    await db.close()
    worker_manager.stop_all()
