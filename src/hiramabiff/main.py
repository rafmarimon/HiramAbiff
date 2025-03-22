#!/usr/bin/env python
"""
Main entry point for the HiramAbiff package.

This module provides high-level functions for using the HiramAbiff
framework to analyze DeFi opportunities across multiple blockchains.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

def get_version() -> str:
    """Return the current version of HiramAbiff."""
    from hiramabiff import __version__
    return __version__

async def analyze_defi_opportunities(
    chains: Optional[List[str]] = None,
    min_yield: float = 5.0,
    min_tvl: float = 1000000,
    max_results: int = 10,
    include_experimental: bool = False,
) -> Dict[str, Any]:
    """
    Analyze DeFi opportunities across multiple blockchains.
    
    Args:
        chains: List of blockchain names to analyze. If None, analyze all supported chains.
        min_yield: Minimum yield percentage to consider.
        min_tvl: Minimum TVL (Total Value Locked) to consider.
        max_results: Maximum number of opportunities to return.
        include_experimental: Whether to include experimental/risky opportunities.
        
    Returns:
        Dict[str, Any]: Results containing opportunities and statistics.
    """
    logger.info(f"Analyzing DeFi opportunities on chains: {chains or 'all'}")
    
    try:
        # Import here to avoid circular imports
        from hiramabiff.agents.defi_agent import DeFiAgent
        
        # Create and run DeFi agent
        agent = DeFiAgent(
            name="MainDeFiAnalyzer",
            min_yield_threshold=min_yield,
            min_tvl_threshold=min_tvl,
            max_opportunities=max_results,
        )
        
        # Run the agent
        results = await agent.run(chains=chains)
        
        logger.info(f"Analysis complete. Found {len(results.get('top_opportunities', []))} opportunities.")
        return results
        
    except Exception as e:
        logger.error(f"Error analyzing DeFi opportunities: {e}")
        raise

def print_report(results: Dict[str, Any]) -> None:
    """
    Print a formatted report of DeFi opportunities.
    
    Args:
        results: Results from analyze_defi_opportunities.
    """
    try:
        # Import here to avoid circular imports
        from hiramabiff.agents.defi_agent import DeFiAgent
        
        # Create a temporary agent just to use the print_report method
        agent = DeFiAgent(name="ReportPrinter")
        agent.print_report(results)
        
    except Exception as e:
        logger.error(f"Error printing report: {e}")
        print("Error printing formatted report. Raw results:")
        print(results)

def main():
    """Command-line entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="HiramAbiff - DeFi Opportunity Analyzer")
    parser.add_argument("--chains", nargs="+", help="Blockchains to analyze (default: all)")
    parser.add_argument("--min-yield", type=float, default=5.0, help="Minimum yield percentage")
    parser.add_argument("--min-tvl", type=float, default=1000000, help="Minimum TVL")
    parser.add_argument("--max-results", type=int, default=10, help="Maximum number of results")
    parser.add_argument("--include-experimental", action="store_true", help="Include experimental opportunities")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"HiramAbiff version {get_version()}")
        return
    
    # Run the analysis
    results = asyncio.run(analyze_defi_opportunities(
        chains=args.chains,
        min_yield=args.min_yield,
        min_tvl=args.min_tvl,
        max_results=args.max_results,
        include_experimental=args.include_experimental,
    ))
    
    # Print the report
    print_report(results)

if __name__ == "__main__":
    main() 