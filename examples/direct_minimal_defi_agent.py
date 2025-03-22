#!/usr/bin/env python
"""
Direct Example Using MinimalDeFiAgent

This script demonstrates how to use the MinimalDeFiAgent class directly
from the source code without requiring package installation.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

def main():
    """Main entry point."""
    try:
        # Import directly from the source
        from hiramabiff.agents.minimal_defi_agent import MinimalDeFiAgent
        
        print("Successfully imported MinimalDeFiAgent from source")
        
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
        print(f"Error importing MinimalDeFiAgent: {e}")
        print("Make sure the source files are properly structured")
        sys.exit(1)
    except Exception as e:
        print(f"Error running example: {e}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 