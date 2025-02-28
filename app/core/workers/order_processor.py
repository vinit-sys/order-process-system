from app.core.logging import worker_logger
from app.services.redis_service import redis_service
from datetime import datetime
import asyncio
import os
from app.core.config import settings
import time
from app.core.workers.base import BaseWorker
import time
import os
from app.tasks.push_order_to_db import push_order_to_db
from app.core.logging import worker_logger
from app.services.redis_service import redis_service
from app.connections.database import db
from app.models.order import OrderStatus
from datetime import datetime
import asyncio
from app.models.managers.orders import OrderManager
import json



class OrderProcessor(BaseWorker):
    def __init__(self, num_processes: int = None):
        super().__init__("OrderProcessor", num_processes)

    def run(self):
        worker_id = os.getpid()
        worker_logger.info(f"Worker started with PID: {worker_id}")
        
        while True:
            try:
                with redis_service.redis_conn.pipeline() as pipe:
                    pipe.lrange("order_queue", 0, settings.BATCH_SIZE - 1)
                    pipe.ltrim("order_queue", settings.BATCH_SIZE, -1)
                    results = pipe.execute()
                    order_ids = results[0]

                if order_ids:
                    worker_logger.info(f"Worker {worker_id} processing {len(order_ids)} orders")
                    asyncio.run(self.process_order_batch([oid.decode() for oid in order_ids]))
                else:
                    time.sleep(0.01)
            except Exception as e:
                worker_logger.error(f"Worker {worker_id} error: {e}", exc_info=True)

    async def process_order_batch(self, orders):
        if not orders:
            return

        try:
            worker_logger.info(f"Processing batch of {len(orders)} orders: {orders}")

            # Process orders
            
            async with db.session() as session:
                order_manager = OrderManager(session)
                await order_manager.update_bulk_orders(order_ids=orders,**{"status": OrderStatus.PROCESSING})
            
                await asyncio.sleep(0.1)
            
                completion_time = datetime.utcnow()
                await order_manager.update_bulk_orders(order_ids=orders,**{"status": OrderStatus.COMPLETED})
            
            with redis_service.redis_conn.pipeline() as pipe:
                pipe.incrby("total_processed", len(orders))
                pipe.execute()

            worker_logger.info(f"Completed batch of orders: {orders}")
                
        except Exception as e:
            worker_logger.error(f"Error processing batch: {e}", exc_info=True)
        finally:
            if db:
                await db.close()

class RedisOrderProcessor(BaseWorker):
    def __init__(self, num_processes: int = None):
        super().__init__("RedisOrderProcessor", num_processes)

    def run(self):
        while True:
            task  = redis_service.redis_conn.lpop("test_check")
            if task:
                try:
                    task_data = json.loads(task)
                    asyncio.run(push_order_to_db(task_data,task_data["order_id"]))
                    print(f"Executed push_order_to_db with result:")
                except Exception as e:
                    print(f"Error executing task: {e}")