#!/usr/bin/env python
"""
HiramAbiff System Runner

This script starts all the HiramAbiff components including the dashboard,
LangChain agents, and any necessary services.
"""

import argparse
import asyncio
import os
import sys
import threading
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger

from src.app import app
from src.core.config import settings
from src.core.logger import setup_logging
from src.agents.langchain_agent import market_analysis_agent
import uvicorn


async def initial_report_generation():
    """Generate an initial market analysis report on startup."""
    try:
        logger.info("Generating initial market analysis report...")
        await market_analysis_agent.generate_market_analysis()
        logger.info("Initial market analysis report generated successfully")
    except Exception as e:
        logger.error(f"Error generating initial market analysis report: {e}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="HiramAbiff System Runner")
    parser.add_argument(
        "--skip-initial-report", 
        action="store_true",
        help="Skip generating an initial market analysis report on startup"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=settings.APP_PORT,
        help=f"Port to run the server on (default: {settings.APP_PORT})"
    )
    return parser.parse_args()


def main():
    """Start all HiramAbiff components."""
    args = parse_args()
    
    # Set up logging
    setup_logging()
    
    logger.info("Starting HiramAbiff System")
    logger.info(f"Environment: {settings.APP_ENV}")
    logger.info(f"Dashboard will be available at: http://{settings.APP_HOST}:{args.port}/dashboard/")
    
    # Check if API keys are configured
    if not os.getenv("OPENAI_API_KEY"):
        logger.warning("OpenAI API key not found in environment variables")
        logger.warning("Market analysis reports may not work correctly")
    
    if not os.getenv("LANGCHAIN_API_KEY"):
        logger.warning("LangChain API key not found in environment variables")
        logger.warning("LangChain tracing will not be available")
    
    # Generate initial report if not skipped
    if not args.skip_initial_report:
        asyncio.run(initial_report_generation())
    
    # Start the web server
    uvicorn.run(
        app,
        host=settings.APP_HOST,
        port=args.port,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main() 