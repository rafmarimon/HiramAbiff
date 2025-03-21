"""
Trading agent module.

This module provides the implementation of a specialized trading agent that
executes trades based on opportunities found by the DeFi agent.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from loguru import logger

from src.agents.base_agent import BaseAgent, AgentStatus
from src.blockchain.solana_client import SolanaClientManager, NetworkType


class TradingAgent(BaseAgent):
    """
    Trading agent for executing trades based on opportunities found by the DeFi agent.
    This agent specializes in optimal trade execution, slippage management, and trade monitoring.
    """
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: str = "TradingAgent",
        solana_network: NetworkType = NetworkType.MAINNET,
        max_slippage: float = 0.5,  # 0.5% max slippage
        execution_retry_count: int = 3,
        cooldown_period: int = 60,  # seconds between trades
    ):
        """
        Initialize the trading agent.
        
        Args:
            agent_id: Unique identifier for the agent.
            name: Human-readable name for the agent.
            solana_network: Solana network to connect to.
            max_slippage: Maximum allowed slippage percentage.
            execution_retry_count: Number of times to retry a failed trade.
            cooldown_period: Seconds to wait between trades.
        """
        super().__init__(agent_id=agent_id, name=name)
        
        self.solana_network = solana_network
        self.max_slippage = max_slippage
        self.execution_retry_count = execution_retry_count
        self.cooldown_period = cooldown_period
        
        # Initialize blockchain client
        self.solana_client = SolanaClientManager(network_type=solana_network)
        
        # Trade execution state
        self.executed_trades = []
        self.pending_trades = []
        self.failed_trades = []
        self.last_trade_time = None
        
        logger.info(f"Initialized trading agent with {solana_network} network")
        logger.info(f"  - Max slippage: {max_slippage}%")
        logger.info(f"  - Retry count: {execution_retry_count}")
        logger.info(f"  - Cooldown period: {cooldown_period}s")
    
    async def run(self, opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute trades based on provided opportunities.
        
        Args:
            opportunities: List of opportunities to potentially trade.
            
        Returns:
            Dict[str, Any]: Results of trade execution.
        """
        logger.info(f"Starting trading agent run with {len(opportunities)} opportunities")
        
        self.pending_trades = opportunities.copy()
        self.executed_trades = []
        self.failed_trades = []
        
        # Process each opportunity
        for opp in opportunities:
            # Check for cooldown period
            if self.last_trade_time and time.time() - self.last_trade_time < self.cooldown_period:
                wait_time = self.cooldown_period - (time.time() - self.last_trade_time)
                logger.info(f"Waiting {wait_time:.2f}s for cooldown between trades")
                await asyncio.sleep(wait_time)
            
            # Execute the trade
            trade_result = await self._execute_trade(opp)
            
            if trade_result["status"] == "executed":
                self.executed_trades.append(trade_result)
                self.last_trade_time = time.time()
            else:
                self.failed_trades.append(trade_result)
        
        # Generate results
        results = self._generate_results()
        logger.info(f"Trading agent run completed with {len(self.executed_trades)} successful trades")
        
        return results
    
    async def _execute_trade(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a trade for a specific opportunity.
        
        Args:
            opportunity: The opportunity to trade.
            
        Returns:
            Dict[str, Any]: Result of the trade execution.
        """
        protocol = opportunity.get("protocol", "unknown")
        chain = opportunity.get("chain", "unknown")
        symbol = opportunity.get("symbol", "unknown")
        
        logger.info(f"Executing trade for {protocol}/{symbol} on {chain}")
        
        # In a real implementation, this would integrate with DEXs and execute the actual trade
        # For this example, we'll simulate the execution with delays and random success/failure
        
        trade_result = {
            "opportunity_id": opportunity.get("id"),
            "protocol": protocol,
            "chain": chain,
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "attempt_count": 0,
            "status": "pending",
            "details": {}
        }
        
        # Simulate trade execution with retries
        for attempt in range(1, self.execution_retry_count + 1):
            trade_result["attempt_count"] = attempt
            
            logger.info(f"Trade execution attempt {attempt}/{self.execution_retry_count}")
            
            # Simulate trade execution time
            await asyncio.sleep(1.0)
            
            # In a real implementation, we would check for slippage, confirm the trade, etc.
            # For simulation purposes, we'll assume 20% of trades fail on first attempt
            # but succeed on retry (simulating network issues or temporary liquidity problems)
            if attempt == 1 and opportunity.get("id", "")[-1] in "01":  # Simple way to fail ~20% of trades initially
                logger.warning(f"Trade execution failed, retrying...")
                continue
            
            # Simulate successful trade
            trade_result["status"] = "executed"
            trade_result["details"] = {
                "execution_time": datetime.now().isoformat(),
                "amount": 100.0,  # Example amount
                "price": opportunity.get("price", 1.0),
                "slippage": 0.1,  # Example slippage percentage
                "fee": 0.05,  # Example fee percentage
                "tx_hash": f"simulated_tx_{int(time.time())}",  # Simulated transaction hash
            }
            
            logger.info(f"Trade executed successfully: {trade_result['details']['tx_hash']}")
            return trade_result
        
        # If we get here, all retries failed
        trade_result["status"] = "failed"
        trade_result["error"] = "Maximum retry count reached"
        
        logger.error(f"Trade execution failed after {self.execution_retry_count} attempts")
        return trade_result
    
    def _generate_results(self) -> Dict[str, Any]:
        """
        Generate result summary from the agent's operations.
        
        Returns:
            Dict[str, Any]: Summary of executed trades.
        """
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "timestamp": datetime.now().isoformat(),
            "total_opportunities": len(self.pending_trades),
            "executed_trades": self.executed_trades,
            "failed_trades": self.failed_trades,
            "success_rate": len(self.executed_trades) / max(1, len(self.pending_trades)) * 100,
            "stats": {
                "avg_slippage": sum(t.get("details", {}).get("slippage", 0) for t in self.executed_trades) / max(1, len(self.executed_trades)),
                "total_amount": sum(t.get("details", {}).get("amount", 0) for t in self.executed_trades),
                "chains": list(set(t.get("chain") for t in self.executed_trades)),
                "protocols": list(set(t.get("protocol") for t in self.executed_trades)),
            }
        }
    
    async def get_trade_status(self, trade_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a specific trade.
        
        Args:
            trade_id: The ID of the trade to check.
            
        Returns:
            Optional[Dict[str, Any]]: Trade details if found, None otherwise.
        """
        # First check executed trades
        for trade in self.executed_trades:
            if trade.get("opportunity_id") == trade_id:
                return trade
        
        # Then check failed trades
        for trade in self.failed_trades:
            if trade.get("opportunity_id") == trade_id:
                return trade
                
        return None
    
    async def close(self) -> None:
        """
        Close connections and clean up resources.
        """
        logger.info("Closing trading agent connections")
        
        # Close blockchain clients
        if hasattr(self, "solana_client"):
            self.solana_client.close()
        
        # Reset state
        self.executed_trades = []
        self.pending_trades = []
        self.failed_trades = []
        
        logger.info("Trading agent connections closed") 