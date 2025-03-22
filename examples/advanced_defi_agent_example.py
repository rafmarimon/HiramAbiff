#!/usr/bin/env python
"""
Advanced DeFi Agent Example

This example demonstrates how to create a specialized DeFi agent that focuses on 
finding arbitrage opportunities and optimal yield strategies on Solana.

The agent performs the following tasks:
1. Fetches yield data from DeFiLlama
2. Queries current token prices
3. Calculates optimal yield farming strategies
4. Identifies potential arbitrage opportunities 
5. Simulates the execution of these strategies
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Add the src directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from loguru import logger

from src.agents.base_agent import BaseAgent
from src.agents.defi_agent import DeFiAgent
from src.blockchain.solana_client import NetworkType, SolanaClientManager
from src.core.config import settings
from src.core.logger import setup_logging
from src.data.defillama import DeFiLlamaClient


class SolanaArbitrageAgent(DeFiAgent):
    """
    Specialized DeFi agent that focuses on finding arbitrage opportunities
    and optimal yield strategies on Solana.
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "SolanaArbitrageAgent",
        min_yield_threshold: float = 3.0,
        min_arb_profit_threshold: float = 0.5,  # Minimum 0.5% profit for arbitrage
        max_opportunities: int = 10,
    ):
        """
        Initialize the Solana Arbitrage Agent.
        
        Args:
            agent_id: Unique identifier for the agent
            name: Human-readable name for the agent
            min_yield_threshold: Minimum APY to consider for yield strategies
            min_arb_profit_threshold: Minimum profit percentage for arbitrage opportunities
            max_opportunities: Maximum number of opportunities to process
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            solana_network=NetworkType.MAINNET,
            min_yield_threshold=min_yield_threshold,
            min_tvl_threshold=100000,  # Lower threshold to find more opportunities
            max_opportunities=max_opportunities,
        )
        
        self.min_arb_profit_threshold = min_arb_profit_threshold
        self.arbitrage_opportunities = []
        self.defillama_client = DeFiLlamaClient()
        
        logger.info(f"Initialized {name} with {min_arb_profit_threshold}% profit threshold")
    
    async def run(self, chains: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run the specialized agent to find arbitrage and yield opportunities.
        
        Args:
            chains: List of blockchain names to analyze (defaults to just Solana)
            
        Returns:
            Dict[str, Any]: Results including opportunities and strategies
        """
        # Override chains to focus only on Solana
        chains = ["Solana"]
        logger.info(f"Starting {self.name} run for {chains}")
        
        try:
            # Run the standard DeFi agent to get yield opportunities
            defi_results = await super().run(chains=chains)
            
            # Find arbitrage opportunities
            await self._find_arbitrage_opportunities()
            
            # Calculate optimal strategies 
            strategies = self._calculate_optimal_strategies()
            
            # Combine results
            results = {
                **defi_results,
                "arbitrage_opportunities": self.arbitrage_opportunities,
                "optimal_strategies": strategies,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Agent run completed with {len(self.arbitrage_opportunities)} arbitrage opportunities")
            return results
            
        except Exception as e:
            logger.exception(f"Error during agent run: {e}")
            raise
    
    async def _find_arbitrage_opportunities(self) -> None:
        """
        Find potential arbitrage opportunities on Solana by comparing prices
        across different DEXs and protocols.
        """
        logger.info("Finding arbitrage opportunities on Solana")
        self.arbitrage_opportunities = []
        
        # This would normally interact with multiple DEXs to get pricing data
        # For this example, we'll simulate finding some opportunities
        
        # Sample tokens to check (in a real implementation, this would be dynamic)
        tokens = ["SOL", "USDC", "BONK", "JUP", "RAY"]
        
        # DEXs to compare (in a real implementation, this would query actual prices)
        dexs = ["Jupiter", "Orca", "Raydium"]
        
        # Simulate finding a few arbitrage opportunities
        for token in tokens:
            # Generate simulated prices across DEXs 
            prices = {
                dex: round(1.0 * (1 + (hash(f"{token}{dex}") % 10) / 100), 6) 
                for dex in dexs
            }
            
            # Find min and max prices
            min_price = min(prices.items(), key=lambda x: x[1])
            max_price = max(prices.items(), key=lambda x: x[1])
            
            # Calculate profit percentage
            profit_pct = ((max_price[1] - min_price[1]) / min_price[1]) * 100
            
            # If profit exceeds threshold, add to opportunities
            if profit_pct >= self.min_arb_profit_threshold:
                opportunity = {
                    "token": token,
                    "buy_dex": min_price[0],
                    "buy_price": min_price[1],
                    "sell_dex": max_price[0],
                    "sell_price": max_price[1],
                    "profit_pct": round(profit_pct, 2),
                    "timestamp": datetime.now().isoformat(),
                }
                self.arbitrage_opportunities.append(opportunity)
                
        # Sort by profit percentage descending
        self.arbitrage_opportunities.sort(key=lambda x: x["profit_pct"], reverse=True)
        
        logger.info(f"Found {len(self.arbitrage_opportunities)} arbitrage opportunities")
    
    def _calculate_optimal_strategies(self) -> List[Dict[str, Any]]:
        """
        Calculate optimal yield farming and investment strategies based on 
        the yield and arbitrage opportunities found.
        
        Returns:
            List[Dict[str, Any]]: List of optimal strategies
        """
        logger.info("Calculating optimal DeFi strategies")
        
        strategies = []
        
        # Strategy 1: Top yielding stable coins
        stable_yields = [
            opp for opp in self.filtered_opportunities 
            if any(stable in opp.get("symbol", "") for stable in ["USD", "USDC", "USDT", "DAI"])
        ]
        
        if stable_yields:
            strategies.append({
                "name": "Stable Coin Yield Farming",
                "description": "Optimal stable coin yield farming strategy",
                "opportunities": stable_yields[:3],
                "expected_apy": sum(opp.get("apy", 0) for opp in stable_yields[:3]) / len(stable_yields[:3]),
                "risk_level": "Low",
                "chain": "Solana"
            })
        
        # Strategy 2: High yield, higher risk
        high_yields = [
            opp for opp in self.filtered_opportunities 
            if opp.get("apy", 0) > self.min_yield_threshold * 2
        ]
        
        if high_yields:
            strategies.append({
                "name": "High APY Strategy",
                "description": "Higher risk, higher reward yield farming",
                "opportunities": high_yields[:3],
                "expected_apy": sum(opp.get("apy", 0) for opp in high_yields[:3]) / len(high_yields[:3]),
                "risk_level": "High",
                "chain": "Solana"
            })
        
        # Strategy 3: Arbitrage combined with yield farming
        if self.arbitrage_opportunities and self.filtered_opportunities:
            # Take top arbitrage and combine with moderate yield
            top_arb = self.arbitrage_opportunities[0]
            moderate_yields = [
                opp for opp in self.filtered_opportunities 
                if self.min_yield_threshold <= opp.get("apy", 0) <= self.min_yield_threshold * 2
            ]
            
            if moderate_yields:
                strategies.append({
                    "name": "Arbitrage + Yield Strategy",
                    "description": f"Execute {top_arb['token']} arbitrage and stake profits in moderate yield farm",
                    "arbitrage": top_arb,
                    "yield_opportunity": moderate_yields[0],
                    "expected_return": top_arb["profit_pct"] + moderate_yields[0].get("apy", 0) / 365,  # Daily return
                    "risk_level": "Medium",
                    "chain": "Solana"
                })
        
        logger.info(f"Calculated {len(strategies)} optimal strategies")
        return strategies
    
    def print_report(self, results: Dict[str, Any]) -> None:
        """
        Print a formatted report of the agent's findings.
        
        Args:
            results: The results from running the agent
        """
        print("\n" + "="*50)
        print(f"🔍 {self.name} REPORT")
        print("="*50)
        
        # Print yield opportunities
        print("\n📈 TOP YIELD OPPORTUNITIES ON SOLANA")
        print("-"*50)
        for i, opp in enumerate(results['top_opportunities'][:5], 1):
            print(f"{i}. {opp['protocol']} - {opp['symbol']}")
            print(f"   APY: {opp['apy']:.2f}% | TVL: ${opp['tvl']:,.2f}")
            print(f"   Pool: {opp['pool']}")
            print()
        
        # Print arbitrage opportunities
        print("\n💰 ARBITRAGE OPPORTUNITIES")
        print("-"*50)
        for i, arb in enumerate(results['arbitrage_opportunities'][:5], 1):
            print(f"{i}. {arb['token']}: Buy on {arb['buy_dex']} at ${arb['buy_price']}, "
                  f"Sell on {arb['sell_dex']} at ${arb['sell_price']}")
            print(f"   Profit: {arb['profit_pct']}%")
            print()
        
        # Print optimal strategies
        print("\n🚀 RECOMMENDED STRATEGIES")
        print("-"*50)
        for i, strategy in enumerate(results['optimal_strategies'], 1):
            print(f"{i}. {strategy['name']} (Risk: {strategy['risk_level']})")
            print(f"   {strategy['description']}")
            if 'expected_apy' in strategy:
                print(f"   Expected APY: {strategy['expected_apy']:.2f}%")
            elif 'expected_return' in strategy:
                print(f"   Expected Daily Return: {strategy['expected_return']:.2f}%")
            print()
        
        print("\n" + "="*50)
        print(f"Report generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50 + "\n")


async def main():
    """
    Main function demonstrating the Solana Arbitrage Agent.
    """
    # Set up logging
    setup_logging()
    logger.info("Starting advanced DeFi agent example")
    
    # Create a specialized arbitrage agent
    agent = SolanaArbitrageAgent(
        name="SolanaYieldMaster",
        min_yield_threshold=5.0,
        min_arb_profit_threshold=0.8,
        max_opportunities=15,
    )
    
    try:
        # Run the agent
        logger.info("Running specialized arbitrage agent")
        results = await agent.execute()
        
        # Print the formatted report
        if results:
            agent.print_report(results)
        else:
            print("No results returned from agent.")
        
        # Close connections
        await agent.close()
        logger.info("Advanced DeFi agent example completed successfully")
        
    except Exception as e:
        logger.exception(f"Error running example: {e}")


if __name__ == "__main__":
    """Run the advanced example."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Example interrupted by user")
    except Exception as e:
        logger.exception(f"Error in example: {e}") 