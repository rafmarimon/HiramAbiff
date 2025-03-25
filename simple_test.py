#!/usr/bin/env python
"""
Simple test script to run the yield dashboard directly
"""

from src.yield_dashboard import create_dashboard

def main():
    # Create the dashboard with demo mode
    app = create_dashboard(demo=True)
    
    # Run the dashboard
    app.run_server(host="localhost", port=8889, debug=True)

if __name__ == "__main__":
    main() 