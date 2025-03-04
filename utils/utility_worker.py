import threading
import time
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
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
        self.scheduled_tasks = []  # List of tasks: (function, interval, last_run, args, kwargs)
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
    
    def start(self):
        logger.info("Starting UtilityWorker scheduler loop.")
        self.scheduler_thread.start()
    
    def _scheduler_loop(self):
        while not self.shutdown_event.is_set():
            now = time.time()
            for i, task in enumerate(self.scheduled_tasks):
                func, interval, last_run, args, kwargs = task
                if now - last_run >= interval:
                    # Update last run time and run the task.
                    self.scheduled_tasks[i] = (func, interval, now, args, kwargs)
                    self.add_task(func, *args, **kwargs)
            time.sleep(1)
    
    def add_task(self, func, *args, **kwargs):
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
        logger.info("Shutting down UtilityWorker.")
        self.shutdown_event.set()
        self.executor.shutdown(wait=wait)
        self.scheduler_thread.join(timeout=5)
        logger.info("UtilityWorker shutdown complete.")

def run_in_background(func):
    """
    Decorator to run a function in the background using the global utility worker.
    """
    def wrapper(*args, **kwargs):
        global utility_worker
        utility_worker.add_task(func, *args, **kwargs)
    return wrapper

# Create a global instance of UtilityWorker.
utility_worker = UtilityWorker(max_workers=4)
utility_worker.start()
