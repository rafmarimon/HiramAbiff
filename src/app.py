"""
Main application entry point for HiramAbiff.
"""

import asyncio
import os
import sys
import threading
import time
from pathlib import Path

# Add the src directory to the path for relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from loguru import logger
import schedule

from src.core.config import settings
from src.core.logger import setup_logging
from src.agents.langchain_agent import market_analysis_agent
from src.web import create_dashboard


def create_app() -> FastAPI:
    """
    Creates the FastAPI application with middleware and routes.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    app = FastAPI(
        title="HiramAbiff",
        description="Chain-Agnostic DeFi Agent",
        version="0.1.0",
        docs_url="/docs" if settings.APP_DEBUG else None,
        redoc_url="/redoc" if settings.APP_DEBUG else None,
        openapi_url="/openapi.json" if settings.APP_DEBUG else None,
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Register API routes
    # app.include_router(api_router, prefix="/api")
    
    @app.get("/")
    async def root():
        """Root endpoint that redirects to the dashboard."""
        return RedirectResponse(url="/dashboard/")
    
    @app.get("/api")
    async def api_root():
        """Root endpoint to check if the API is running."""
        return {
            "status": "online",
            "app": "HiramAbiff",
            "version": "0.1.0", 
            "environment": settings.APP_ENV,
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint for monitoring."""
        return {"status": "healthy"}
    
    # Create the Dash app
    if settings.WEB_DASHBOARD_ENABLED:
        dash_app = create_dashboard()
        
        # Mount the Dash app
        app.mount("/dashboard", dash_app.server)
        logger.info("Dashboard mounted at /dashboard")
        
        # Mount static files
        static_dir = Path(__file__).parent / "web" / "static"
        if static_dir.exists():
            app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
            logger.info(f"Static files mounted from {static_dir}")
    
    return app


def start_scheduler():
    """Start the scheduler for periodic tasks like report generation."""
    logger.info("Starting scheduler for periodic tasks")
    
    # Schedule the market analysis report generation
    schedule.every().day.at(settings.REPORT_GENERATION_TIME).do(generate_report)
    
    # Run the scheduler in a loop
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


async def generate_report():
    """Generate a new market analysis report."""
    logger.info("Generating scheduled market analysis report")
    try:
        await market_analysis_agent.generate_market_analysis()
        logger.info("Scheduled market analysis report generated successfully")
    except Exception as e:
        logger.error(f"Error generating scheduled market analysis report: {e}")


# Create the application
app = create_app()


if __name__ == "__main__":
    """
    Run the application directly when script is executed.
    """
    # Set up logging
    setup_logging()
    
    logger.info(f"Starting HiramAbiff in {settings.APP_ENV} mode")
    
    # Start the scheduler in a background thread
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    logger.info("Scheduler started in background thread")
    
    # Start the web server
    uvicorn.run(
        "src.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 