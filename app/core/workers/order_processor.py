from app.core.logging import worker_logger
from app.services.redis_service import redis_service
from datetime import datetime
import asyncio
import os
from app.core.config import settings
import time
from app.core.workers.base import BaseWorker
from app.tasks.order_save import push_order_to_pipeline
from app.connections.database import db
from app.models.order import OrderStatus
from app.models.managers.orders import OrderManager
import json


class OrderProcessor(BaseWorker):
    def __init__(self, num_processes: int = None):
        """Initialize the OrderProcessor worker."""
        super().__init__("OrderProcessor", num_processes)

    def run(self):
        """Main worker loop that processes orders from the Redis queue."""
        worker_id = os.getpid()
        worker_logger.info(f"Worker started with PID: {worker_id}")

        while True:
            try:
                # Fetch a batch of order IDs from the Redis queue
                with redis_service.redis_conn.pipeline() as pipe:
                    pipe.lrange("order_queue", 0, settings.BATCH_SIZE - 1)  # Get orders
                    pipe.ltrim(
                        "order_queue", settings.BATCH_SIZE, -1
                    )  # Remove processed orders
                    results = pipe.execute()
                    order_ids = results[0]

                if order_ids:
                    worker_logger.info(
                        f"Worker {worker_id} processing {len(order_ids)} orders"
                    )
                    asyncio.run(
                        self.process_order_batch([oid.decode() for oid in order_ids])
                    )
                else:
                    time.sleep(0.01)  # Sleep briefly if no orders are available
            except Exception as e:
                worker_logger.error(f"Worker {worker_id} error: {e}", exc_info=True)

    async def process_order_batch(self, orders):
        """Process a batch of orders asynchronously."""
        if not orders:
            return

        try:
            worker_logger.info(f"Processing batch of {len(orders)} orders: {orders}")

            async with db.session() as session:
                order_manager = OrderManager(session)

                # Update order status to PROCESSING
                await order_manager.update_bulk_orders(
                    order_ids=orders, **{"status": OrderStatus.PROCESSING}
                )

                await asyncio.sleep(0.1)  # Simulate processing time

                # Update order status to COMPLETED
                completion_time = datetime.utcnow()
                await order_manager.update_bulk_orders(
                    order_ids=orders, **{"status": OrderStatus.COMPLETED}
                )

            # Update processed count in Redis
            with redis_service.redis_conn.pipeline() as pipe:
                pipe.incrby("total_processed", len(orders))
                pipe.execute()

            worker_logger.info(f"Completed batch of orders: {orders}")

        except Exception as e:
            worker_logger.error(f"Error processing batch: {e}", exc_info=True)
        finally:
            if db:
                await db.close()  # Ensure database connection is closed


class RedisOrderProcessor(BaseWorker):
    def __init__(self, num_processes: int = None):
        """Initialize the RedisOrderProcessor worker."""
        super().__init__("RedisOrderProcessor", num_processes)

    def run(self):
        """Continuously fetch and process tasks from Redis."""
        while True:
            task = redis_service.redis_conn.lpop(
                "push_order_to_pipeline"
            )  # Get next task
            if task:
                try:
                    task_data = json.loads(task)
                    asyncio.run(
                        push_order_to_pipeline(task_data["order_id"])
                    )  # Process order
                    print(
                        f"Executed push_order_to_pipeline for order ID: {task_data['order_id']}"
                    )
                except Exception as e:
                    print(f"Error executing task: {e}")
