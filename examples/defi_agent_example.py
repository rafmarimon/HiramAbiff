#!/usr/bin/env python
"""
Example script demonstrating how to use the DeFi agent.

This script shows how to initialize and run the DeFi agent to fetch and analyze
DeFi opportunities from various sources, with a focus on Solana.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the src directory to the path for relative imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger

from src.agents.defi_agent import DeFiAgent
from src.blockchain.solana_client import NetworkType
from src.core.config import settings
from src.core.logger import setup_logging


async def main():
    """
    Main function that demonstrates DeFi agent usage.
    """
    # Set up logging
    setup_logging()
    logger.info("Starting DeFi agent example")
    
    # Create a DeFi agent with custom parameters
    agent = DeFiAgent(
        name="SolanaYieldFinder",
        solana_network=NetworkType.MAINNET,  # Use mainnet for real data
        min_yield_threshold=3.0,  # Look for yields above 3% APY
        min_tvl_threshold=500000,  # Minimum $500k TVL
        max_opportunities=5,  # Return top 5 opportunities
    )
    
    # Run the agent to analyze all chains
    logger.info("Running agent for all chains")
    all_chains_result = await agent.execute()
    
    # Print the results in a readable format
    if all_chains_result:
        print("\n=== Top DeFi Opportunities Across All Chains ===")
        print(f"Found {all_chains_result['opportunities_found']} opportunities")
        print(f"Filtered to {all_chains_result['opportunities_filtered']} high-quality opportunities")
        
        print("\nTop Opportunities:")
        for i, opp in enumerate(all_chains_result['top_opportunities'], 1):
            print(f"{i}. {opp['chain']} - {opp['protocol']} - {opp['symbol']}")
            print(f"   APY: {opp['apy']:.2f}% | TVL: ${opp['tvl']:,.2f}")
            print(f"   Pool: {opp['pool']}")
            print()
            
        print("\nStats:")
        print(f"Average APY: {all_chains_result['stats']['avg_apy']:.2f}%")
        print(f"Total TVL: ${all_chains_result['stats']['total_tvl']:,.2f}")
        print(f"Chains analyzed: {', '.join(all_chains_result['stats']['chains'])}")
        print(f"Protocols found: {', '.join(all_chains_result['stats']['protocols'][:5])}...")
    
    # Now focus just on Solana
    logger.info("Running agent specifically for Solana")
    solana_result = await agent.analyze_chain("Solana")
    
    # Print Solana-specific results
    if solana_result:
        print("\n=== Top DeFi Opportunities on Solana ===")
        print(f"Found {solana_result['opportunities_filtered']} high-quality opportunities")
        
        print("\nTop Opportunities on Solana:")
        for i, opp in enumerate(solana_result['top_opportunities'], 1):
            print(f"{i}. {opp['protocol']} - {opp['symbol']}")
            print(f"   APY: {opp['apy']:.2f}% | TVL: ${opp['tvl']:,.2f}")
            print(f"   Pool: {opp['pool']}")
            print()
    
    # Close connections
    await agent.close()
    logger.info("DeFi agent example completed")


if __name__ == "__main__":
    """Run the example."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    except Exception as e:
        logger.exception(f"Error in example: {e}") 