import logging
import sys
import os

LOG_FILE = "give_my_time_back.log"

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
        
    return logger

log = setup_logger()
