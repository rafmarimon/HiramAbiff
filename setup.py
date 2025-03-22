#!/usr/bin/env python
"""
Setup script for HiramAbiff.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Core requirements
requirements = [
    "fastapi>=0.100.0",
    "uvicorn>=0.23.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "httpx>=0.24.0",
    "asyncio>=3.4.3",
    "pandas>=2.0.0",
    "numpy>=1.24.0",
    "scipy>=1.10.0",
    "web3>=6.6.0",
    "solana>=0.29.0",
    "base58>=2.1.0",
    "scikit-learn>=1.3.0",
    "cryptography>=41.0.0",
    "loguru>=0.7.0",
    "tqdm>=4.65.0",
    "click>=8.1.0",
    "typer>=0.9.0",
    "rich>=13.4.0",
    # Visualization dependencies
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "pillow>=10.0.0",
]

# Extra requirements
extras_require = {
    "dev": [
        "pytest>=7.3.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.1.0",
        "black>=23.3.0",
        "isort>=5.12.0",
        "mypy>=1.3.0",
        "flake8>=6.0.0",
    ],
    "ml": [
        "tensorflow>=2.12.0; python_version < '3.12'",
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "ray>=2.5.0; python_version < '3.12'",
        "mlflow>=2.4.0",
    ],
    "ui": [
        "streamlit>=1.23.0",
        "plotly>=5.14.0",
        "dash>=2.10.0",
    ],
}

setup(
    name="hiramabiff",
    version="0.1.0",
    author="HiramAbiff Team",
    author_email="info@hiramabiff.io",
    description="Chain-agnostic DeFi agent with a focus on Solana",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/HiramAbiff",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/HiramAbiff/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        "console_scripts": [
            "hiramabiff=hiramabiff.cli:main",
        ],
    },
) 