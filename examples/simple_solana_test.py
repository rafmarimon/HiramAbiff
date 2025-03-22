#!/usr/bin/env python
"""
Simple script to test connectivity to Solana testnet.
This serves as a minimal example to verify Solana package installation and connectivity.
"""

import os
import time
import asyncio
import secrets
import traceback
from loguru import logger

# Solana imports
from solders.pubkey import Pubkey
from solders.keypair import Keypair
import solana.rpc.async_api

# Set up logging
logger.add("solana_test.log", rotation="10 MB")

logger.info("Starting Solana testnet connectivity test")

async def test_connection():
    """Test connection to Solana testnet with basic RPC calls."""
    # Connect to Solana testnet
    url = "https://api.testnet.solana.com"
    logger.info(f"Testing connection to Solana testnet at {url}")
    
    client = solana.rpc.async_api.AsyncClient(url)
    
    try:
        # Test getting version
        version = await client.get_version()
        logger.info(f"Solana version: {version}")
        
        # Generate a new keypair (using the correct method for the latest solders library)
        seed = secrets.token_bytes(32)
        keypair = Keypair.from_seed(bytes(seed))
        public_key = keypair.pubkey()
        logger.info(f"Generated test keypair with public key: {public_key}")
        
        # Test getting account balance (should be 0 for a new key)
        balance = await client.get_balance(public_key)
        logger.info(f"Balance for {public_key}: {balance}")
        
        # Test getting recent blockhash
        blockhash = await client.get_latest_blockhash()
        logger.info(f"Recent blockhash: {blockhash}")
        
        # Check cluster status differently since get_health is not available
        cluster_nodes = await client.get_cluster_nodes()
        logger.info(f"Cluster has {len(cluster_nodes.value)} nodes")
        
    finally:
        # Always close the client
        await client.close()
        logger.info("Connection closed")

try:
    logger.info("Running Solana connectivity test")
    asyncio.run(test_connection())
    logger.info("Test completed successfully")
except Exception as e:
    logger.error(f"Error during test: {str(e)}")
    logger.error(f"\n{traceback.format_exc()}")
finally:
    logger.info("Test finished") 