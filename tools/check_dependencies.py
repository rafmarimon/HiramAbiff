#!/usr/bin/env python
"""
Dependency Checker for HiramAbiff

This script checks if all required dependencies for the HiramAbiff project
are installed correctly and in the correct versions. It also checks if the
environment variables are set properly.

Usage:
    python check_dependencies.py
"""

import sys
import os
import importlib
import subprocess
from pathlib import Path

# Define color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BLUE = "\033[94m"
BOLD = "\033[1m"

def print_header(text):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'=' * 70}{RESET}")
    print(f"{BLUE}{BOLD} {text}{RESET}")
    print(f"{BLUE}{BOLD}{'=' * 70}{RESET}\n")

def print_success(text):
    """Print a success message"""
    print(f"{GREEN}✓ {text}{RESET}")

def print_warning(text):
    """Print a warning message"""
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_error(text):
    """Print an error message"""
    print(f"{RED}✗ {text}{RESET}")

def print_info(text):
    """Print an info message"""
    print(f"{BLUE}ℹ {text}{RESET}")

def check_python_version():
    """Check if Python version is compatible"""
    print_header("Checking Python Version")
    
    py_version = sys.version_info
    min_version = (3, 8)
    recommended_version = (3, 10)
    
    if py_version < min_version:
        print_error(f"Python version {py_version.major}.{py_version.minor} is not supported. "
                   f"Minimum required version is {min_version[0]}.{min_version[1]}")
        return False
    elif py_version < recommended_version:
        print_warning(f"Python version {py_version.major}.{py_version.minor} is supported, "
                     f"but {recommended_version[0]}.{recommended_version[1]} or newer is recommended for best performance")
        return True
    else:
        print_success(f"Python version {py_version.major}.{py_version.minor}.{py_version.micro} is compatible")
        return True
    
def get_requirements():
    """Get requirements from requirements.txt"""
    try:
        requirements_path = Path(__file__).parent.parent / "requirements.txt"
        with open(requirements_path, 'r') as f:
            requirements = [line.strip() for line in f.readlines() 
                           if line.strip() and not line.startswith('#')]
        return requirements
    except FileNotFoundError:
        print_error("requirements.txt not found")
        return []

def check_package_installed(package_name):
    """Check if a package is installed using importlib instead of pkg_resources"""
    try:
        # Split package name to handle versioning syntax like 'package==1.0'
        base_name = package_name.split('==')[0].split('>=')[0].strip()
        
        # Try to import the module - this works for most packages
        importlib.import_module(base_name)
        return True
    except ImportError:
        # Some packages have different import names than PyPI names
        # Add special cases here
        special_cases = {
            'python-dotenv': 'dotenv',
            'PyYAML': 'yaml',
            'scikit-learn': 'sklearn',
            'solders': 'solders',
            # Add more mappings as needed
        }
        
        if base_name in special_cases:
            try:
                importlib.import_module(special_cases[base_name])
                return True
            except ImportError:
                return False
        
        return False

def get_package_version(package_name):
    """Get the version of an installed package without using pkg_resources"""
    try:
        # Split package name to handle versioning syntax
        base_name = package_name.split('==')[0].split('>=')[0].strip()
        
        # Special cases for version attributes
        version_attr_map = {
            'numpy': 'numpy.__version__',
            'pandas': 'pandas.__version__',
            'solana': 'solana.version.__version__',
            'solders': 'solders.__version__',
            'loguru': 'loguru.__version__',
            # Add more mappings as needed
        }
        
        module = importlib.import_module(base_name)
        
        if base_name in version_attr_map:
            # Use eval to access nested attributes
            return eval(version_attr_map[base_name])
        
        # Try common version attributes
        for attr in ['__version__', 'version', 'VERSION', '__VERSION__']:
            if hasattr(module, attr):
                return getattr(module, attr)
        
        return "Unknown"
    except (ImportError, AttributeError):
        return "Unknown"

def check_dependencies():
    """Check if all dependencies are installed correctly using importlib"""
    print_header("Checking Dependencies")
    
    try:
        # First check if setuptools is installed (needed for pkg_resources)
        print_info("Checking for setuptools...")
        try:
            import pkg_resources
            print_success("setuptools is installed")
            pkg_resources_available = True
        except ImportError:
            print_warning("setuptools is not installed - using importlib for package checking")
            print_info("Consider installing setuptools: pip install setuptools")
            pkg_resources_available = False
            
        requirements = get_requirements()
        if not requirements:
            return False
        
        all_installed = True
        critical_packages = ['solders', 'solana', 'loguru', 'pandas', 'numpy', 'websockets']
        
        for req in requirements:
            package_name = req.split('==')[0].split('>=')[0].strip()
            
            try:
                if pkg_resources_available:
                    # Use pkg_resources if available
                    is_installed = pkg_resources.get_distribution(package_name) is not None
                    if is_installed:
                        version = pkg_resources.get_distribution(package_name).version
                else:
                    # Fall back to importlib
                    is_installed = check_package_installed(package_name)
                    version = get_package_version(package_name) if is_installed else "Not installed"
                
                if is_installed:
                    print_success(f"{package_name} is installed (version: {version})")
                    
                    # Check specific packages that we know might cause issues
                    if package_name == 'solders':
                        # Verify solders functionality
                        try:
                            import solders.keypair
                            solders.keypair.Keypair
                            print_success("  solders.keypair.Keypair class is available")
                        except (ImportError, AttributeError) as e:
                            print_error(f"  Error with solders.keypair.Keypair: {e}")
                            all_installed = False
                            
                    elif package_name == 'solana':
                        # Verify solana functionality
                        try:
                            import solana.rpc.api
                            solana.rpc.api.Client
                            print_success("  solana.rpc.api.Client class is available")
                        except (ImportError, AttributeError) as e:
                            print_error(f"  Error with solana.rpc.api.Client: {e}")
                            all_installed = False
                            
                else:
                    if package_name in critical_packages:
                        print_error(f"{package_name} is NOT installed (REQUIRED)")
                        all_installed = False
                    else:
                        print_warning(f"{package_name} is NOT installed")
                        
            except Exception as e:
                print_error(f"Error checking {package_name}: {e}")
                if package_name in critical_packages:
                    all_installed = False
        
        return all_installed
    except Exception as e:
        print_error(f"Error checking dependencies: {e}")
        return False

def check_environment_variables():
    """Check if required environment variables are set"""
    print_header("Checking Environment Variables")
    
    env_vars = {
        'SOLANA_RPC_URL': 'Main Solana RPC URL',
        'SOLANA_RPC_URL_TESTNET': 'Solana Testnet RPC URL',
        'SOLANA_RPC_URL_DEVNET': 'Solana Devnet RPC URL',
        'LOG_LEVEL': 'Logging level',
        'LOG_FILE': 'Log file location'
    }
    
    optional_vars = {
        'DEFILLAMA_API_URL': 'DeFiLlama API URL',
        'DEFILLAMA_API_KEY': 'DeFiLlama API Key'
    }
    
    all_required_set = True
    
    # Check required env vars
    for var, description in env_vars.items():
        if var in os.environ and os.environ[var]:
            print_success(f"{var} is set ({description})")
        else:
            print_error(f"{var} is NOT set ({description})")
            all_required_set = False
    
    # Check optional env vars
    for var, description in optional_vars.items():
        if var in os.environ and os.environ[var]:
            print_success(f"{var} is set ({description})")
        else:
            print_warning(f"{var} is NOT set ({description}) - Optional")
    
    return all_required_set

def check_git_setup():
    """Check if git is set up correctly"""
    print_header("Checking Git Setup")
    
    try:
        # Check if git is installed
        result = subprocess.run(['git', '--version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        
        if result.returncode == 0:
            git_version = result.stdout.strip()
            print_success(f"Git is installed: {git_version}")
            
            # Check if current directory is a git repository
            repo_path = Path(__file__).parent.parent
            result = subprocess.run(['git', 'status'], 
                                   cwd=repo_path,
                                   stdout=subprocess.PIPE, 
                                   stderr=subprocess.PIPE,
                                   text=True)
            
            if result.returncode == 0:
                print_success("HiramAbiff directory is a Git repository")
                return True
            else:
                print_warning("HiramAbiff directory is NOT a Git repository")
                print_info("Consider initializing a Git repository to track your code changes")
                return True
        else:
            print_warning("Git is NOT installed")
            print_info("Consider installing Git for better code management")
            return False
    except FileNotFoundError:
        print_warning("Git is NOT installed")
        print_info("Consider installing Git for better code management")
        return False

def check_hiramabiff_installable():
    """Check if HiramAbiff package is installed in development mode"""
    print_header("Checking HiramAbiff Installation")
    
    try:
        import hiramabiff
        print_success("HiramAbiff package is installed")
        return True
    except ImportError:
        print_warning("HiramAbiff package is NOT installed")
        print_info("Consider installing in development mode with: pip install -e .")
        return False

def main():
    """Main function to run all checks"""
    print_header("HiramAbiff Dependency Checker")
    print(f"{BLUE}This tool checks if your environment is correctly set up for HiramAbiff{RESET}\n")
    
    python_ok = check_python_version()
    dependencies_ok = check_dependencies()
    env_vars_ok = check_environment_variables()
    git_ok = check_git_setup()
    hiramabiff_ok = check_hiramabiff_installable()
    
    print_header("Summary")
    
    if python_ok:
        print_success("Python version check passed")
    else:
        print_error("Python version check failed")
    
    if dependencies_ok:
        print_success("All required dependencies are installed")
    else:
        print_error("Some required dependencies are missing")
    
    if env_vars_ok:
        print_success("All required environment variables are set")
    else:
        print_error("Some required environment variables are missing")
    
    if git_ok:
        print_success("Git setup check passed")
    else:
        print_warning("Git setup check warning (non-critical)")
    
    if hiramabiff_ok:
        print_success("HiramAbiff package is installed")
    else:
        print_warning("HiramAbiff package is not installed")
    
    overall_status = python_ok and dependencies_ok and env_vars_ok
    
    if overall_status:
        print("\n" + GREEN + BOLD + "✓ Your environment is correctly set up for HiramAbiff!" + RESET)
    else:
        print("\n" + YELLOW + BOLD + "⚠ Your environment needs some adjustments before using HiramAbiff." + RESET)
        print(YELLOW + "Please fix the issues mentioned above and run this script again." + RESET)
    
    return 0 if overall_status else 1

if __name__ == "__main__":
    sys.exit(main()) 