import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging():
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Main application logger
    logger = logging.getLogger("order_processor")
    logger.setLevel(logging.INFO)

    # Create handlers
    main_handler = RotatingFileHandler(
        'logs/app.log', 
        maxBytes=10*1024*1024,
        backupCount=5
    )
    worker_handler = RotatingFileHandler(
        'logs/workers.log',
        maxBytes=10*1024*1024,
        backupCount=5
    )

    # Create formatters
    log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    main_handler.setFormatter(log_format)
    worker_handler.setFormatter(log_format)

    logger.addHandler(main_handler)

    # Worker logger
    worker_logger = logging.getLogger("order_worker")
    worker_logger.setLevel(logging.INFO)
    worker_logger.addHandler(worker_handler)

    return logger, worker_logger

logger, worker_logger = setup_logging()