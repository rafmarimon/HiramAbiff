#!/usr/bin/env python3
"""
Market Dashboard Runner

This script starts the market dashboard for the HiramAbiff project.
"""

import os
import argparse
import logging
import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from flask import Flask, send_from_directory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Dashboard settings
DEFAULT_HOST = os.getenv("DASHBOARD_HOST", "localhost")
DEFAULT_PORT = int(os.getenv("MARKET_DASHBOARD_PORT", "8890"))

def create_dashboard():
    """
    Create the market dashboard.
    
    Returns:
        dash.Dash: The dashboard application
    """
    # Create the app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="HiramAbiff Market Dashboard",
        suppress_callback_exceptions=True,
        server=False,
    )
    
    # Layout
    app.layout = html.Div([
        dbc.Container([
            html.H1("HiramAbiff Market Dashboard", className="my-4"),
            
            html.Div([
                html.H3("Redirecting to Yield Dashboard"),
                html.P([
                    "This is a placeholder for the market dashboard. ",
                    "The full functionality is available in the yield dashboard ",
                    "which includes all market data plus yield farming opportunities."
                ]),
                html.P([
                    "Visit the yield dashboard at: ",
                    html.A("http://localhost:8889/", href="http://localhost:8889/", target="_blank")
                ]),
                html.Hr(),
                html.P([
                    "In the next phase of development, this dashboard will be expanded with: ",
                    html.Ul([
                        html.Li("Advanced market analytics"),
                        html.Li("Trading views and technical analysis"),
                        html.Li("Order book visualization"),
                        html.Li("DeFi market-wide metrics"),
                        html.Li("Integration with multiple data sources"),
                    ])
                ]),
                
                dcc.Interval(id="redirect-interval", interval=5000, n_intervals=0),
                dcc.Location(id="url-redirect", refresh=True)
            ], className="p-5 bg-light rounded border")
        ])
    ])
    
    # Redirect callback
    @app.callback(
        dash.Output("url-redirect", "href"),
        dash.Input("redirect-interval", "n_intervals")
    )
    def redirect_to_yield_dashboard(n_intervals):
        # Only redirect after 5 seconds (1 interval)
        if n_intervals == 1:
            return "http://localhost:8889/"
        return dash.no_update
    
    return app

def setup_static_routes(server):
    """
    Set up routes for static files.
    
    Args:
        server: Flask server instance
    """
    @server.route('/static/js/<path:path>')
    def serve_js(path):
        return send_from_directory('static/js', path)
    
    @server.route('/static/css/<path:path>')
    def serve_css(path):
        return send_from_directory('static/css', path)
    
    @server.route('/static/img/<path:path>')
    def serve_img(path):
        return send_from_directory('static/img', path)

def main():
    """Main function to run the dashboard."""
    parser = argparse.ArgumentParser(description="Run the HiramAbiff Market Dashboard")
    parser.add_argument("--host", type=str, default=DEFAULT_HOST, help="Host to run the dashboard on")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to run the dashboard on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Create the dashboard
    app = create_dashboard()
    
    # Set up static routes
    setup_static_routes(app.server)
    
    # Log dashboard info
    logger.info(f"Starting market dashboard on {args.host}:{args.port}")
    logger.info(f"Debug mode: {args.debug}")
    
    # Run the app
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    main() 