from typing import List
from app.core.workers.base import BaseWorker
import logging

logger = logging.getLogger(__name__)

class WorkerManager:
    def __init__(self):
        self.workers: List[BaseWorker] = []

    def add_worker(self, worker: BaseWorker):
        self.workers.append(worker)

    def start_all(self):
        for worker in self.workers:
            worker.start()

    def stop_all(self):
        for worker in self.workers:
            worker.stop()

# Global instance
worker_manager = WorkerManager()