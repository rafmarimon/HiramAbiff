#!/usr/bin/env python
"""
Agent collaboration example script.

This script demonstrates how multiple specialized agents can work together
in the HiramAbiff system, with the DeFi agent finding opportunities and
the Trading agent executing trades.
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
from src.agents.trading_agent import TradingAgent
from src.blockchain.solana_client import NetworkType
from src.core.config import settings
from src.core.logger import setup_logging


async def main():
    """
    Main function demonstrating agent collaboration.
    """
    # Set up logging
    setup_logging()
    logger.info("Starting agent collaboration example")
    
    # Create a DeFi agent to find opportunities
    defi_agent = DeFiAgent(
        name="OpportunityFinder",
        solana_network=NetworkType.MAINNET,
        min_yield_threshold=5.0,  # Look for yields above 5% APY
        min_tvl_threshold=1000000,  # Minimum $1M TVL
        max_opportunities=5,  # Return top 5 opportunities
    )
    
    # Create a Trading agent to execute trades
    trading_agent = TradingAgent(
        name="TradeExecutor",
        solana_network=NetworkType.MAINNET,
        max_slippage=0.5,  # 0.5% max slippage
        execution_retry_count=3,
        cooldown_period=60,  # 60s between trades
    )
    
    try:
        # Step 1: Run the DeFi agent to find opportunities
        logger.info("Step 1: Finding DeFi opportunities with DeFi agent")
        defi_result = await defi_agent.execute()
        
        if not defi_result or not defi_result.get("top_opportunities"):
            logger.warning("No opportunities found by DeFi agent")
            return
        
        opportunities = defi_result.get("top_opportunities", [])
        logger.info(f"DeFi agent found {len(opportunities)} potential opportunities")
        
        # Print summary of found opportunities
        print("\n=== Opportunities Found by DeFi Agent ===")
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp['chain']} - {opp['protocol']} - {opp['symbol']}")
            print(f"   APY: {opp['apy']:.2f}% | TVL: ${opp['tvl']:,.2f}")
        print()
        
        # Step 2: Pass the opportunities to the Trading agent
        logger.info("Step 2: Executing trades with Trading agent")
        trading_result = await trading_agent.execute(opportunities)
        
        if not trading_result:
            logger.warning("Trading agent execution failed")
            return
        
        # Print summary of trade execution
        print("\n=== Trades Executed by Trading Agent ===")
        print(f"Opportunities analyzed: {trading_result['total_opportunities']}")
        print(f"Successful trades: {len(trading_result['executed_trades'])}")
        print(f"Failed trades: {len(trading_result['failed_trades'])}")
        print(f"Success rate: {trading_result['success_rate']:.2f}%")
        print()
        
        print("Details of executed trades:")
        for i, trade in enumerate(trading_result['executed_trades'], 1):
            print(f"{i}. {trade['chain']} - {trade['protocol']} - {trade['symbol']}")
            print(f"   Status: {trade['status']}")
            print(f"   TX Hash: {trade['details'].get('tx_hash', 'N/A')}")
            print(f"   Amount: ${trade['details'].get('amount', 0):,.2f}")
            print(f"   Slippage: {trade['details'].get('slippage', 0):.2f}%")
            print(f"   Fee: {trade['details'].get('fee', 0):.2f}%")
            print()
        
        # Step 3: Demonstrate checking trade status
        if trading_result['executed_trades']:
            trade_id = trading_result['executed_trades'][0]['opportunity_id']
            logger.info(f"Step 3: Checking status of trade {trade_id}")
            
            trade_status = await trading_agent.get_trade_status(trade_id)
            print(f"\n=== Status of Trade {trade_id} ===")
            if trade_status:
                print(f"Status: {trade_status['status']}")
                print(f"Protocol: {trade_status['protocol']}")
                print(f"Symbol: {trade_status['symbol']}")
                print(f"Timestamp: {trade_status['timestamp']}")
                if "details" in trade_status:
                    print("Details:")
                    for key, value in trade_status['details'].items():
                        print(f"  {key}: {value}")
            else:
                print("Trade not found")
    
    finally:
        # Clean up resources
        logger.info("Closing agent connections")
        await defi_agent.close()
        await trading_agent.close()
    
    logger.info("Agent collaboration example completed")


if __name__ == "__main__":
    """Run the example."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    except Exception as e:
        logger.exception(f"Error in example: {e}") 