from typing import List
from app.core.workers.base import BaseWorker
import logging

logger = logging.getLogger(__name__)


class WorkerManager:
    """Manages multiple worker instances for execution control."""

    def __init__(self):
        """Initialize an empty list of workers."""
        self.workers: List[BaseWorker] = []

    def add_worker(self, worker: BaseWorker):
        """Add a worker to the manager."""
        self.workers.append(worker)

    def start_all(self):
        """Start all registered workers."""
        for worker in self.workers:
            worker.start()

    def stop_all(self):
        """Stop all registered workers."""
        for worker in self.workers:
            worker.stop()


# Global instance of WorkerManager to manage workers across the application
worker_manager = WorkerManager()
