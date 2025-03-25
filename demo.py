#!/usr/bin/env python3
"""
HiramAbiff Demo Script

This script runs a comprehensive demonstration of the HiramAbiff platform,
including both the market and yield farming dashboards with wallet integration
and monetization features.
"""

import os
import sys
import time
import signal
import subprocess
import argparse
import webbrowser
import threading

# Define dashboard ports
MARKET_DASHBOARD_PORT = 8890
YIELD_DASHBOARD_PORT = 8889

# Process holders
market_process = None
yield_process = None

def run_market_dashboard(port=MARKET_DASHBOARD_PORT, debug=False, open_browser=True):
    """
    Run the market dashboard.
    
    Args:
        port: Port to run the dashboard on
        debug: Whether to run in debug mode
        open_browser: Whether to open the dashboard in a browser
    """
    print(f"Starting market dashboard on port {port}...")
    
    # Build the command
    cmd = [sys.executable, "run_market_dashboard.py", "--port", str(port)]
    if debug:
        cmd.append("--debug")
    
    # Start the process
    global market_process
    market_process = subprocess.Popen(cmd)
    
    # Wait for the dashboard to start
    time.sleep(2)
    
    # Open browser if requested
    if open_browser:
        webbrowser.open(f"http://localhost:{port}/")
    
    return market_process

def run_yield_dashboard(port=YIELD_DASHBOARD_PORT, debug=False, open_browser=True, demo=True):
    """
    Run the yield farming dashboard.
    
    Args:
        port: Port to run the dashboard on
        debug: Whether to run in debug mode
        open_browser: Whether to open the dashboard in a browser
        demo: Whether to run with demo data
    """
    print(f"Starting yield farming dashboard on port {port}...")
    
    # Build the command
    cmd = [
        sys.executable, 
        "run_yield_dashboard.py", 
        "--port", str(port),
        "--host", "localhost"
    ]
    if debug:
        cmd.append("--debug")
    if demo:
        cmd.append("--demo")
    
    # Start the process
    global yield_process
    yield_process = subprocess.Popen(cmd)
    
    # Wait for the dashboard to start
    time.sleep(2)
    
    # Open browser if requested
    if open_browser:
        webbrowser.open(f"http://localhost:{port}/")
    
    return yield_process

def cleanup(signum=None, frame=None):
    """Clean up processes on exit."""
    print("\nCleaning up...")
    
    if market_process:
        print("Stopping market dashboard...")
        market_process.terminate()
    
    if yield_process:
        print("Stopping yield farming dashboard...")
        yield_process.terminate()
    
    print("Cleanup complete.")
    
    if signum is not None:
        sys.exit(0)

def start_dashboards(run_market=True, run_yield=True, open_browsers=True, debug=False):
    """
    Start the dashboards.
    
    Args:
        run_market: Whether to run the market dashboard
        run_yield: Whether to run the yield farming dashboard
        open_browsers: Whether to open the dashboards in browsers
        debug: Whether to run in debug mode
    """
    # Register signal handlers for clean shutdown
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Start dashboards in threads
    threads = []
    
    if run_market:
        market_thread = threading.Thread(
            target=run_market_dashboard,
            kwargs={"port": MARKET_DASHBOARD_PORT, "debug": debug, "open_browser": open_browsers}
        )
        threads.append(market_thread)
    
    if run_yield:
        yield_thread = threading.Thread(
            target=run_yield_dashboard,
            kwargs={"port": YIELD_DASHBOARD_PORT, "debug": debug, "open_browser": open_browsers, "demo": True}
        )
        threads.append(yield_thread)
    
    # Start threads
    for thread in threads:
        thread.start()
    
    # Wait for threads to complete
    for thread in threads:
        thread.join()

def print_welcome_message():
    """Print welcome message."""
    print("""
╔════════════════════════════════════════════════════════════╗
║                                                            ║
║              HiramAbiff Platform Demonstration             ║
║                                                            ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  This demo will start both the market and yield farming    ║
║  dashboards, showcasing the full functionality of the      ║
║  HiramAbiff platform.                                      ║
║                                                            ║
║  Key Features:                                             ║
║  - Real-time market data visualization                     ║
║  - Yield farming opportunity detection                     ║
║  - Portfolio tracking and analysis                         ║
║  - Wallet integration (Phantom/Solflare)                   ║
║  - Monetization with fee management                        ║
║  - AI-powered insights and recommendations                 ║
║                                                            ║
║  The dashboards will be available at:                      ║
║  - Market Dashboard:   http://localhost:8890/              ║
║  - Yield Dashboard:    http://localhost:8889/              ║
║                                                            ║
║  Press Ctrl+C to exit the demo.                            ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="HiramAbiff Platform Demo")
    parser.add_argument("--market-only", action="store_true", help="Run only the market dashboard")
    parser.add_argument("--yield-only", action="store_true", help="Run only the yield farming dashboard")
    parser.add_argument("--no-browser", action="store_true", help="Don't open browsers automatically")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    
    args = parser.parse_args()
    
    # Determine which dashboards to run
    run_market = not args.yield_only
    run_yield = not args.market_only
    
    # Print welcome message
    print_welcome_message()
    
    try:
        # Start dashboards
        start_dashboards(
            run_market=run_market,
            run_yield=run_yield,
            open_browsers=not args.no_browser,
            debug=args.debug
        )
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
            # Check if processes are still alive
            if run_market and market_process and market_process.poll() is not None:
                print("Market dashboard stopped unexpectedly.")
                run_market = False
            
            if run_yield and yield_process and yield_process.poll() is not None:
                print("Yield farming dashboard stopped unexpectedly.")
                run_yield = False
            
            # Exit if all processes have stopped
            if not run_market and not run_yield:
                print("All dashboards have stopped. Exiting...")
                break
                
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    finally:
        cleanup()

if __name__ == "__main__":
    main() 