#!/usr/bin/env python
"""
Setup script for HiramAbiff.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="hiramabiff",
    version="0.1.0",
    author="Rafael Marimon",
    author_email="your.email@example.com",
    description="Chain-agnostic DeFi agent with a focus on Solana",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rafmarimon/HiramAbiff",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "hiramabiff-testnet=scripts.solana_testnet_launcher:main",
        ],
    },
) 