import logging
import os
from logging.handlers import RotatingFileHandler
from config import LOG_LEVEL, LOG_FILE


def setup_logging():
    """Configure logging with stdout and optional file handlers."""
    logger = logging.getLogger("parser")
    logger.setLevel(LOG_LEVEL)

    formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s")

    # Stdout handler
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(LOG_LEVEL)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # File handler (if LOG_FILE is set)
    if LOG_FILE:
        log_dir = os.path.dirname(LOG_FILE)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(LOG_LEVEL)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
