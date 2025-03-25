#!/usr/bin/env python3
"""
Verification script for the HiramAbiff Yield Dashboard.

This script checks that all components of the dashboard are properly installed
and functioning correctly.
"""

import os
import sys
import requests
import importlib
import subprocess
from pathlib import Path

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def check_module(module_name):
    """Check if a Python module is installed."""
    try:
        importlib.import_module(module_name)
        print(f"✅ Module {module_name} is installed")
        return True
    except ImportError:
        print(f"❌ Module {module_name} is NOT installed")
        return False

def check_file(file_path):
    """Check if a file exists."""
    path = Path(file_path)
    if path.exists():
        print(f"✅ File {file_path} exists")
        return True
    else:
        print(f"❌ File {file_path} does NOT exist")
        return False

def check_directory(dir_path):
    """Check if a directory exists."""
    path = Path(dir_path)
    if path.exists() and path.is_dir():
        print(f"✅ Directory {dir_path} exists")
        return True
    else:
        print(f"❌ Directory {dir_path} does NOT exist")
        return False

def check_api_endpoint(endpoint, method="GET", data=None):
    """Check if an API endpoint is accessible."""
    url = f"http://localhost:8889{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data or {}, timeout=5)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            print(f"✅ API endpoint {endpoint} is accessible")
            return True
        else:
            print(f"❌ API endpoint {endpoint} returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error accessing API endpoint {endpoint}: {e}")
        return False

def check_dashboard_status():
    """Check if the dashboard is running."""
    try:
        result = subprocess.run(
            ["lsof", "-i", ":8889"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if "Python" in result.stdout:
            print("✅ Dashboard is running on port 8889")
            return True
        else:
            print("❌ Dashboard is NOT running on port 8889")
            return False
    except Exception as e:
        print(f"❌ Error checking dashboard status: {e}")
        return False

def main():
    """Run all verification checks."""
    print_section("HiramAbiff Yield Dashboard Verification")
    
    # Check if dashboard is running
    dashboard_running = check_dashboard_status()
    if not dashboard_running:
        print("\n⚠️  Dashboard is not running. Please start it with: python run_yield_dashboard_enhanced.py --demo")
        sys.exit(1)
    
    # Check required modules
    print_section("Required Python Modules")
    modules = ["flask", "requests", "pandas", "numpy"]
    modules_ok = all(check_module(module) for module in modules)
    
    # Check OpenAI module (optional)
    openai_ok = check_module("openai")
    if openai_ok:
        if os.getenv("OPENAI_API_KEY"):
            print("✅ OPENAI_API_KEY environment variable is set")
        else:
            print("⚠️  OPENAI_API_KEY environment variable is NOT set (required for AI insights)")
    
    # Check required directories
    print_section("Required Directories")
    directories = ["src", "static", "templates", "cache", "portfolios"]
    directories_ok = all(check_directory(directory) for directory in directories)
    
    # Check required files
    print_section("Required Files")
    files = [
        "run_yield_dashboard_enhanced.py",
        "static/css/styles.css",
        "static/js/wallet_connector.js",
        "templates/dashboard.html",
        "src/blockchain/wallet_integration.py",
        "src/monetization/fee_manager.py",
        "src/data_aggregator.py",
        "src/opportunity_detector.py",
        "src/trade_simulator.py"
    ]
    files_ok = all(check_file(file) for file in files)
    
    # Check API endpoints
    print_section("API Endpoints")
    endpoints_ok = check_api_endpoint("/")
    endpoints_ok &= check_api_endpoint("/api/opportunities")
    endpoints_ok &= check_api_endpoint("/api/wallet/data")
    endpoints_ok &= check_api_endpoint("/api/fees/calculate", method="POST", data={"profit_amount": 100})
    
    # Try to generate insights if OpenAI is available
    if openai_ok and os.getenv("OPENAI_API_KEY"):
        print("\nTesting AI insights generation...")
        insights_ok = check_api_endpoint("/api/generate-insights", method="POST")
    else:
        insights_ok = True  # Skip this check if OpenAI is not available
    
    # Final result
    print_section("Verification Result")
    all_ok = dashboard_running and modules_ok and directories_ok and files_ok and endpoints_ok and insights_ok
    
    if all_ok:
        print("🎉 All checks passed! The dashboard is properly installed and running.")
        print("\nYou can access it at: http://localhost:8889/")
    else:
        print("⚠️  Some checks failed. Please fix the issues above and try again.")
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main()) 