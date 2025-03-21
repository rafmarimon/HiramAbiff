"""
Main application entry point for HiramAbiff.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the path for relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.core.config import settings
from src.core.logger import setup_logging


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
    
    return app


app = create_app()


if __name__ == "__main__":
    """
    Run the application directly when script is executed.
    """
    logger.info(f"Starting HiramAbiff in {settings.APP_ENV} mode")
    uvicorn.run(
        "src.app:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 