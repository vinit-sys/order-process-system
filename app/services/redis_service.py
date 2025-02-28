from redis import Redis
from rq import Queue
from ..core.config import settings

class RedisService:
    def __init__(self):
        self.redis_conn = Redis.from_url(settings.REDIS_URL)
        self.order_queue = Queue('orders', connection=self.redis_conn)

    async def add_order_to_queue(self, order_id):
        retry_count = 0
        while retry_count < 3:
            with self.redis_conn.pipeline() as pipe:
                pipe.rpush("order_queue", order_id)
                pipe.execute()
            
            queue_position = self.redis_conn.lpos("order_queue", order_id)
            if queue_position is not None:
                return queue_position
            retry_count += 1
        return None

    def get_queue_status(self):
        queue_length = self.redis_conn.llen("order_queue")
        pending_orders = self.redis_conn.lrange("order_queue", 0, 9)
        total_processed = self.redis_conn.get("total_processed")
        
        return {
            "queue_length": queue_length,
            "pending_orders": [order_id.decode() for order_id in pending_orders],
            "total_processed": int(total_processed.decode()) if total_processed else 0
        }

redis_service = RedisService()