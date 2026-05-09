import logging
import sys
import os
import queue

LOG_FILE = "give_my_time_back.log"
log_queue = queue.Queue()

class QueueHandler(logging.Handler):
    """Custom logging handler that sends logs to a queue for the GUI."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)

def setup_logger():
    logger = logging.getLogger("give_my_time_back")
    logger.setLevel(logging.INFO)
    
    # Prevent duplicate handlers if setup is called multiple times
    if not logger.handlers:
        formatter = logging.Formatter('%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        
        # File handler
        file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Queue handler for GUI
        queue_handler = QueueHandler(log_queue)
        queue_handler.setFormatter(formatter)
        logger.addHandler(queue_handler)
        
    return logger

log = setup_logger()
