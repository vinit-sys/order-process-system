from multiprocessing import Process, Event, cpu_count
import os
import logging
import traceback

logger = logging.getLogger(__name__)

class BaseWorker:
    def __init__(self, name: str, num_processes: int = None):
        self.name = name
        self.processes = []
        self.stop_event = Event()
        # If num_processes not specified, use CPU count - 1 (leave one for main process)
        self.num_processes = num_processes or max(1, cpu_count() - 1)

    def start(self):
        """Start the worker processes"""
        self.stop_event.clear()
        
        for i in range(self.num_processes):
            process = Process(
                target=self._run,
                name=f"{self.name}-{i}",
            )
            print(f"stadsfsfdksfsdlfshfgldsfhdksghlsdhl")
            process.start()
            self.processes.append(process)
            logger.info(f"{process.name} started with PID {process.pid}")

    def stop(self):
        """Stop all worker processes"""
        self.stop_event.set()
        for process in self.processes:
            process.join(timeout=10)
            if process.is_alive():
                process.terminate()
        self.processes.clear()
        logger.info(f"{self.name} workers stopped")

    def _run(self):
        """Wrapper for the run method"""
        try:
            self.run()
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error in {self.name}: {e}")

    def run(self):
        """Override this method in child classes"""
        raise NotImplementedError