#!/usr/bin/env python3
"""
Simplified Yield Farming Dashboard Runner

This script starts a simplified yield farming dashboard for testing.
"""

import os
import argparse
import logging
from flask import Flask, send_from_directory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dashboard settings
DEFAULT_HOST = os.getenv("DASHBOARD_HOST", "0.0.0.0")
DEFAULT_PORT = int(os.getenv("YIELD_DASHBOARD_PORT", "8889"))

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
    <head>
        <title>HiramAbiff Yield Dashboard</title>
    </head>
    <body>
        <h1>HiramAbiff Yield Dashboard</h1>
        <p>This is a simplified version of the dashboard for testing purposes.</p>
        <p>The full dashboard will be implemented once we resolve the Dash connection issues.</p>
    </body>
    </html>
    """

@app.route('/static/js/<path:path>')
def serve_js(path):
    return send_from_directory('static/js', path)

@app.route('/static/css/<path:path>')
def serve_css(path):
    return send_from_directory('static/css', path)

@app.route('/static/img/<path:path>')
def serve_img(path):
    return send_from_directory('static/img', path)

def main():
    """Main function to run the dashboard."""
    parser = argparse.ArgumentParser(description="Run the HiramAbiff Yield Farming Dashboard")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Host to run the dashboard on")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to run the dashboard on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    
    args = parser.parse_args()
    
    # Log dashboard info
    logger.info(f"Starting simplified yield farming dashboard on {args.host}:{args.port}")
    logger.info(f"Debug mode: {args.debug}")
    logger.info(f"Demo portfolio: {args.demo}")
    
    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main() 