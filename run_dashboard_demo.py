#!/usr/bin/env python
"""
Simple Dashboard Runner Script for Demo

This script starts only the dashboard part of HiramAbiff without the LangChain integration.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from src.core.config import settings
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from src.web.dashboard.app import create_dashboard

def create_app() -> FastAPI:
    """
    Creates a simplified FastAPI application with the dashboard.
    
    Returns:
        FastAPI: The configured FastAPI application
    """
    app = FastAPI(
        title="HiramAbiff Demo",
        description="Chain-Agnostic DeFi Agent Dashboard Demo",
        version="0.1.0",
    )

    # Set up CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint that redirects to the dashboard."""
        return RedirectResponse(url="/dashboard/")
    
    # Create the Dash app
    dash_app = create_dashboard()
    
    # Mount the Dash app
    app.mount("/dashboard", dash_app.server)
    print("Dashboard mounted at /dashboard")
    
    # Mount static files
    static_dir = Path("src/web/static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        print(f"Static files mounted from {static_dir}")
    
    return app

if __name__ == "__main__":
    """
    Run the application directly.
    """
    app = create_app()
    
    print(f"Starting HiramAbiff Demo Dashboard")
    print(f"Dashboard will be available at: http://{settings.APP_HOST}:{settings.APP_PORT}/dashboard/")
    
    uvicorn.run(
        app,
        host=settings.APP_HOST,
        port=settings.APP_PORT,
    ) 