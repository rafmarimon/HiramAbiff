"""
Logging configuration for the HiramAbiff application.
"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from loguru import logger


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


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configures logging for the application.
    
    Args:
        log_level: The logging level to use (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Get log level from environment or use provided default
    log_level = os.environ.get("LOG_LEVEL", log_level).upper()
    
    # Create logs directory if it doesn't exist
    # First try to find the project root
    current_file = Path(__file__)
    if "src" in current_file.parts:
        # If we're in a src directory, assume project root is two levels up
        project_root = current_file.parent.parent.parent
    else:
        # Otherwise use the current directory
        project_root = Path.cwd()
    
    log_dir = project_root / "logs"
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
                "sink": log_dir / "hiramabiff.log",
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

    # Custom logging for common libraries
    for _log in ["uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"]:
        _logger = logging.getLogger(_log)
        if _logger:  # Check if logger exists
            _logger.handlers = [InterceptHandler()]
            _logger.propagate = False

    # Log initialization
    logger.info(f"Logging initialized. Level: {log_level}")


# Add a convenience function to get a logger
def get_logger(name: str) -> logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The name for the logger
        
    Returns:
        A logger instance
    """
    return logger.bind(name=name) 