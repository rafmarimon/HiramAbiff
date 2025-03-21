"""
Logging configuration for the HiramAbiff application.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger

from .config import settings


class InterceptHandler(logging.Handler):
    """
    Intercepts standard logging messages and redirects them to Loguru.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """
        Intercepts log records and passes them to loguru.
        Args:
            record: The logging record to intercept.
        """
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where the logged message originated
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """
    Configures logging for the application.
    """
    # Create logs directory if it doesn't exist
    log_dir = settings.BASE_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Configure loguru
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Get log level from settings
    log_level = settings.LOG_LEVEL.upper()

    # Configure loguru loggers
    config = {
        "handlers": [
            {
                "sink": sys.stdout,
                "format": log_format,
                "level": log_level,
                "colorize": True,
            },
            {
                "sink": log_dir / f"hiramabiff_{settings.APP_ENV}.log",
                "format": log_format,
                "level": log_level,
                "rotation": "100 MB",
                "retention": "1 week",
                "compression": "zip",
            },
        ],
        "extra": {"app_name": "HiramAbiff"},
    }

    # Apply configuration
    logger.configure(**config)

    # Intercept all standard library loggers
    for logger_name in logging.root.manager.loggerDict:
        logging.getLogger(logger_name).handlers = [InterceptHandler()]

    # Custom logging for MongoDB, Uvicorn, etc.
    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        logging.getLogger(_log).handlers = [InterceptHandler()]
        logging.getLogger(_log).propagate = False

    # Add console logger as default
    logger.info(f"Logging initialized. Level: {log_level}")


# Initialize logging when module is imported
setup_logging() 