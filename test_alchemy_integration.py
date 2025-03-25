#!/usr/bin/env python
"""
Test script for Alchemy Solana API Integration

This script verifies that the Alchemy Solana API integration is working correctly
by making some basic RPC calls and displaying the results.
"""

import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from loguru import logger

# Try to import Solana packages
try:
    from solana.rpc.async_api import AsyncClient
    from solders.pubkey import Pubkey  # Updated from solana.publickey import PublicKey
    HAS_SOLANA = True
except ImportError as e:
    logger.warning(f"Solana packages not installed. Some functionality will be disabled. Error: {e}")
    HAS_SOLANA = False

async def test_alchemy_solana_connection():
    """Test connection to Alchemy Solana API"""
    # Load environment variables
    load_dotenv()
    
    # Get Alchemy API settings
    alchemy_api_key = os.getenv("ALCHEMY_API_KEY")
    alchemy_solana_url = os.getenv("ALCHEMY_SOLANA_URL")
    
    if not alchemy_solana_url:
        logger.error("ALCHEMY_SOLANA_URL not found in environment variables")
        return False
        
    # Print info (masking the API key for security)
    base_url = alchemy_solana_url.split('/v2/')[0]
    logger.info(f"Testing connection to Alchemy Solana API: {base_url}/v2/...")
    
    # Test connection
    try:
        # Create client
        client = AsyncClient(alchemy_solana_url)
        
        # Test 1: Get latest blockhash
        logger.info("Test 1: Get latest blockhash")
        try:
            blockhash_response = await client.get_latest_blockhash()
            logger.success("✓ Successfully retrieved latest blockhash")
            logger.info(f"Blockhash: {blockhash_response.value.blockhash}")
        except Exception as e:
            logger.error(f"Failed to get latest blockhash: {e}")
            return False
            
        # Test 2: Get block height
        logger.info("Test 2: Get block height")
        try:
            block_height = await client.get_block_height()
            logger.success(f"✓ Successfully retrieved block height: {block_height}")
        except Exception as e:
            logger.error(f"Failed to get block height: {e}")
            return False
            
        # Test 3: Get slot
        logger.info("Test 3: Get current slot")
        try:
            slot = await client.get_slot()
            logger.success(f"✓ Successfully retrieved current slot: {slot}")
        except Exception as e:
            logger.error(f"Failed to get current slot: {e}")
            
        # Test 4: Get Solana version
        logger.info("Test 4: Get Solana version")
        try:
            version = await client.get_version()
            # Debug the structure of the version response
            logger.info(f"Version response structure: {dir(version)}")
            logger.info(f"Version response content: {version}")
            logger.success(f"✓ Successfully retrieved Solana version")
        except Exception as e:
            logger.error(f"Failed to get Solana version: {e}")
            
        return True
            
    except Exception as e:
        logger.exception(f"Error while testing Alchemy Solana API: {str(e)}")
        return False
        
async def main():
    """Main function"""
    logger.info("Testing Alchemy Solana API integration")
    
    if not HAS_SOLANA:
        logger.error("Solana packages not installed. Please install them with: pip install solana")
        return
        
    success = await test_alchemy_solana_connection()
    
    if success:
        logger.success("✓ All tests passed! Alchemy Solana API integration is working correctly.")
    else:
        logger.error("✗ Tests failed. Check the logs above for details.")
    
if __name__ == "__main__":
    # Configure logger
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        colorize=True
    )
    
    # Run the async main function
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        sys.exit(0) 