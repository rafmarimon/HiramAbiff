#!/usr/bin/env python
"""
Example Script Using HiramAbiff Package

This script demonstrates how to use the HiramAbiff package
to analyze DeFi opportunities.
"""

import asyncio
import sys

def main():
    """Main entry point."""
    try:
        # Import the package
        from hiramabiff import __version__
        from hiramabiff.agents import MinimalDeFiAgent
        
        print(f"HiramAbiff package version: {__version__}")
        
        # Create a DeFi agent
        agent = MinimalDeFiAgent(
            name="YieldHunterDemo",
            min_yield_threshold=5.0,
            min_tvl_threshold=500000,
            max_opportunities=5,
        )
        
        # Run the agent async
        async def run_agent():
            results = await agent.run(chains=["Solana", "Ethereum"])
            if results:
                agent.print_report(results)
                
        # Run the async function
        asyncio.run(run_agent())
        
        print("Example completed successfully")
        
    except ImportError as e:
        print(f"Error importing HiramAbiff package: {e}")
        print("Make sure the package is installed with: pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"Error running example: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 