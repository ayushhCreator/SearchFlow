"""
Logging Configuration

This module sets up structured logging for the application.
"""

import logging
import sys

from app.core.config import settings


def setup_logging():
    """Configure application logging"""

    # Create logger
    logger = logging.getLogger("searchflow")
    logger.setLevel(settings.LOG_LEVEL)

    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.LOG_LEVEL)

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(handler)

    return logger
