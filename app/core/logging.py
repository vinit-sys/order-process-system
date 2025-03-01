import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logging():
    """Sets up logging for the application and workers with rotating file handlers."""

    log_directory = "logs"

    # Create the logs directory if it doesn't exist
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    # Main application logger
    logger = logging.getLogger("order_processor")
    logger.setLevel(logging.INFO)  # Set logging level to INFO

    # Create rotating file handlers to limit log file size and maintain backups
    main_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB per log file
        backupCount=5,  # Keep up to 5 old log files
    )
    worker_handler = RotatingFileHandler(
        "logs/workers.log",
        maxBytes=10 * 1024 * 1024,  # 10 MB per log file
        backupCount=5,  # Keep up to 5 old log files
    )

    # Create a common log format
    log_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    main_handler.setFormatter(log_format)
    worker_handler.setFormatter(log_format)

    # Attach handler to the main application logger
    logger.addHandler(main_handler)

    # Worker-specific logger
    worker_logger = logging.getLogger("order_worker")
    worker_logger.setLevel(logging.INFO)
    worker_logger.addHandler(worker_handler)

    return logger, worker_logger


# Initialize loggers
logger, worker_logger = setup_logging()
