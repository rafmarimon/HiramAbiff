#!/usr/bin/env python
"""
Dashboard Runner Script

This script starts the HiramAbiff dashboard with the LangChain integration.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from src.app import app
from src.core.config import settings
from src.core.logger import setup_logging
import uvicorn


def main():
    """Start the dashboard."""
    # Set up logging
    setup_logging()
    
    logger.info("Starting HiramAbiff Dashboard")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Dashboard will be available at: http://{settings.APP_HOST}:{settings.APP_PORT}/dashboard/")
    
    # Check if API keys are configured
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OpenAI API key not found in environment variables")
        logger.warning("Market analysis reports may not work correctly")
    
    if not os.getenv("LANGCHAIN_API_KEY"):
        logger.warning("LangChain API key not found in environment variables")
        logger.warning("LangChain tracing will not be available")
    
    # Start the web server
    uvicorn.run(
        app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main() 