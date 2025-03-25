#!/usr/bin/env python
"""
Test Solana Imports

A simple script to test that we can correctly import the Solana modules.
"""

import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
    colorize=True
)

logger.info("Testing Solana imports...")

try:
    logger.info("Importing from solana.rpc.async_api...")
    from solana.rpc.async_api import AsyncClient
    logger.success("✓ Successfully imported AsyncClient")
except ImportError as e:
    logger.error(f"✗ Failed to import AsyncClient: {e}")

try:
    logger.info("Importing from solana.publickey...")
    from solana.publickey import PublicKey
    logger.success("✓ Successfully imported PublicKey")
except ImportError as e:
    logger.error(f"✗ Failed to import PublicKey: {e}")

try:
    logger.info("Importing from solders.keypair...")
    from solders.keypair import Keypair
    logger.success("✓ Successfully imported Keypair")
except ImportError as e:
    logger.error(f"✗ Failed to import Keypair: {e}")

logger.info("Import test complete") 