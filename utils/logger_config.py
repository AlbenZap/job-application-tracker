"""
Logging configuration for the Job Application Tracker
"""

import logging
from datetime import datetime
import os


def setup_logger():
    """Configure logger with file and console handlers"""
    
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_filename = f'logs/app_{datetime.now().strftime("%Y%m%d")}.log'
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logger initialized")
    
    return logger
