# HiramAbiff Tools

This directory contains various utility scripts and tools to help with development, debugging, and managing the HiramAbiff project.

## Available Tools

### Development Tools

1. **check_dependencies.py**
   - A utility to check if all required dependencies are installed correctly
   - Verifies Python version, package installations, environment variables, and Git setup
   - Provides a detailed report of any issues found
   - Usage: `python tools/check_dependencies.py`

### Debugging Tools

Coming soon:

1. **log_analyzer.py** - A tool to analyze and parse log files
2. **performance_profiler.py** - A tool to profile and analyze performance of agents

### Deployment Tools

Coming soon:

1. **docker_helper.py** - Utilities for managing Docker deployments
2. **cloud_deployer.py** - Tools for deploying to cloud environments

## Usage

Most tools can be run directly from the command line:

```bash
# From the project root directory
python tools/check_dependencies.py
```

## Contributing

Feel free to add your own tools to this directory! If you create a useful utility:

1. Follow the existing naming pattern
2. Include detailed docstrings explaining what the tool does
3. Add proper error handling and logging
4. Update this README with information about your tool 