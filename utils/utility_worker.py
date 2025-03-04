import threading
import queue
import time
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Optional: add a console handler if not configured elsewhere
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class UtilityWorker:
    """
    UtilityWorker runs background tasks using a ThreadPoolExecutor and
    supports scheduling of periodic tasks.
    """
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.shutdown_event = threading.Event()
        self.scheduled_tasks = []  # List of tasks: (function, interval, last_run_time, args, kwargs)
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
    
    def start(self):
        """Start the background scheduler loop."""
        logger.info("Starting UtilityWorker scheduler loop.")
        self.scheduler_thread.start()
    
    def _scheduler_loop(self):
        """Check and run scheduled tasks periodically."""
        while not self.shutdown_event.is_set():
            now = time.time()
            for i, task in enumerate(self.scheduled_tasks):
                func, interval, last_run, args, kwargs = task
                if now - last_run >= interval:
                    # Update last run time and run the task
                    self.scheduled_tasks[i] = (func, interval, now, args, kwargs)
                    self.add_task(func, *args, **kwargs)
            time.sleep(1)
    
    def add_task(self, func, *args, **kwargs):
        """
        Add a task to be executed in the background.
        """
        logger.info("Adding task: %s", func.__name__)
        self.executor.submit(self._run_task, func, *args, **kwargs)
    
    def _run_task(self, func, *args, **kwargs):
        try:
            logger.info("Running task: %s", func.__name__)
            return func(*args, **kwargs)
        except Exception as e:
            logger.error("Error in task %s: %s", func.__name__, e, exc_info=True)
    
    def schedule_task(self, func, interval, *args, **kwargs):
        """
        Schedule a task to run every `interval` seconds.
        """
        logger.info("Scheduling task: %s to run every %s seconds", func.__name__, interval)
        self.scheduled_tasks.append((func, interval, time.time(), args, kwargs))
    
    def shutdown(self, wait=True):
        """Shut down the executor and scheduler thread."""
        logger.info("Shutting down UtilityWorker.")
        self.shutdown_event.set()
        self.executor.shutdown(wait=wait)
        self.scheduler_thread.join(timeout=5)
        logger.info("UtilityWorker shutdown complete.")


def run_in_background(func):
    """
    Decorator to run a function in the background via the global utility worker.
    """
    def wrapper(*args, **kwargs):
        global utility_worker
        utility_worker.add_task(func, *args, **kwargs)
    return wrapper


# Create a global instance of UtilityWorker.
utility_worker = UtilityWorker(max_workers=4)
utility_worker.start()

# Example usage if running this module directly.
if __name__ == '__main__':
    def sample_task(name):
        time.sleep(2)
        logger.info("Task %s completed", name)
    
    utility_worker.add_task(sample_task, "TestTask")
    utility_worker.schedule_task(sample_task, 10, "PeriodicTask")
    
    # Run for 30 seconds then shutdown.
    time.sleep(30)
    utility_worker.shutdown()
