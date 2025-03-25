#!/usr/bin/env python
"""
Trade Simulator for HiramAbiff

This module simulates yield farming strategies and tracks mock portfolios
without requiring real blockchain transactions.
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta
import math
import random

from src.data_aggregator import data_aggregator
from src.opportunity_detector import opportunity_detector

# Setup portfolio storage
PORTFOLIO_DIR = Path("portfolios")
PORTFOLIO_DIR.mkdir(exist_ok=True)

class YieldStrategy:
    """
    Represents a yield farming strategy with specific parameters.
    """
    
    def __init__(
        self,
        strategy_id: str = None,
        name: str = None,
        protocol: str = None,
        symbol: str = None,
        pool_id: str = None,
        initial_investment: float = 1000.0,
        apy: float = 10.0,
        duration_days: int = 365,
        compound_frequency: str = "daily",  # daily, weekly, monthly
        risk_level: str = "Medium"
    ):
        """
        Initialize a yield farming strategy.
        
        Args:
            strategy_id: Unique ID for the strategy
            name: Human-readable name for the strategy
            protocol: DeFi protocol (e.g., "Raydium")
            symbol: Token symbol (e.g., "SOL-USDC")
            pool_id: Pool identifier
            initial_investment: Initial investment amount in USD
            apy: Expected Annual Percentage Yield
            duration_days: Strategy duration in days
            compound_frequency: How often returns are compounded
            risk_level: Estimated risk level
        """
        self.strategy_id = strategy_id or f"strategy-{uuid.uuid4()}"
        self.name = name or f"{protocol} {symbol} Strategy"
        self.protocol = protocol
        self.symbol = symbol
        self.pool_id = pool_id
        self.initial_investment = initial_investment
        self.apy = apy
        self.duration_days = duration_days
        self.compound_frequency = compound_frequency
        self.risk_level = risk_level
        
        # Calculate compound periods based on frequency
        if compound_frequency == "daily":
            self.compounds_per_year = 365
        elif compound_frequency == "weekly":
            self.compounds_per_year = 52
        elif compound_frequency == "monthly":
            self.compounds_per_year = 12
        else:
            self.compounds_per_year = 1  # Default to yearly
        
        # Derived metrics
        self.daily_rate = apy / 100 / 365
        self.creation_time = datetime.now()
    
    def calculate_returns(self, days: int = None) -> Dict[str, float]:
        """
        Calculate expected returns for this strategy.
        
        Args:
            days: Number of days to calculate returns for (defaults to strategy duration)
            
        Returns:
            Dict[str, float]: Dict with various return metrics
        """
        if days is None:
            days = self.duration_days
        
        # Calculate simple interest (no compounding)
        simple_interest = self.initial_investment * (self.apy / 100) * (days / 365)
        
        # Calculate compound interest based on compounding frequency
        periods = days / 365 * self.compounds_per_year
        compound_interest = self.initial_investment * ((1 + (self.apy / 100) / self.compounds_per_year) ** periods) - self.initial_investment
        
        # Calculate final values
        simple_final = self.initial_investment + simple_interest
        compound_final = self.initial_investment + compound_interest
        
        return {
            "days": days,
            "initial_investment": self.initial_investment,
            "simple_interest": simple_interest,
            "compound_interest": compound_interest,
            "simple_final": simple_final,
            "compound_final": compound_final,
            "simple_roi": (simple_interest / self.initial_investment) * 100,
            "compound_roi": (compound_interest / self.initial_investment) * 100
        }
    
    def simulate_daily_returns(self, variance: float = 0.1) -> List[Dict[str, Any]]:
        """
        Simulate daily returns with some variance for realistic fluctuations.
        
        Args:
            variance: Amount of daily variance in APY (0.1 = 10%)
            
        Returns:
            List[Dict[str, Any]]: Daily return data
        """
        daily_data = []
        current_value = self.initial_investment
        
        start_date = self.creation_time.date()
        
        for day in range(self.duration_days):
            current_date = start_date + timedelta(days=day)
            
            # Add some random variance to the daily rate
            variance_factor = 1.0 + random.uniform(-variance, variance)
            daily_rate_with_variance = self.daily_rate * variance_factor
            
            # Calculate daily return
            daily_return = current_value * daily_rate_with_variance
            
            # Update current value based on compounding frequency
            if self.compound_frequency == "daily":
                current_value += daily_return
            elif self.compound_frequency == "weekly" and day % 7 == 0:
                # Compound on weekly boundaries
                weekly_return = sum(d["daily_return"] for d in daily_data[-7:] if len(daily_data) >= 7)
                current_value += weekly_return
            elif self.compound_frequency == "monthly" and day % 30 == 0:
                # Compound on monthly boundaries
                monthly_return = sum(d["daily_return"] for d in daily_data[-30:] if len(daily_data) >= 30)
                current_value += monthly_return
            
            daily_data.append({
                "day": day,
                "date": current_date.isoformat(),
                "daily_rate": daily_rate_with_variance,
                "daily_return": daily_return,
                "current_value": current_value,
                "profit": current_value - self.initial_investment,
                "roi": ((current_value - self.initial_investment) / self.initial_investment) * 100
            })
        
        return daily_data
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert strategy to dictionary for storage."""
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "protocol": self.protocol,
            "symbol": self.symbol,
            "pool_id": self.pool_id,
            "initial_investment": self.initial_investment,
            "apy": self.apy,
            "duration_days": self.duration_days,
            "compound_frequency": self.compound_frequency,
            "risk_level": self.risk_level,
            "daily_rate": self.daily_rate,
            "creation_time": self.creation_time.isoformat(),
            "expected_returns": self.calculate_returns()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'YieldStrategy':
        """Create strategy from dictionary."""
        strategy = cls(
            strategy_id=data.get("strategy_id"),
            name=data.get("name"),
            protocol=data.get("protocol"),
            symbol=data.get("symbol"),
            pool_id=data.get("pool_id"),
            initial_investment=data.get("initial_investment", 1000.0),
            apy=data.get("apy", 10.0),
            duration_days=data.get("duration_days", 365),
            compound_frequency=data.get("compound_frequency", "daily"),
            risk_level=data.get("risk_level", "Medium")
        )
        return strategy
    
    @classmethod
    def from_opportunity(cls, opportunity: Dict[str, Any], investment: float = 1000.0, duration_days: int = 365) -> 'YieldStrategy':
        """Create strategy from an opportunity."""
        return cls(
            name=f"{opportunity.get('project', 'Unknown')} {opportunity.get('symbol', 'Unknown')} Strategy",
            protocol=opportunity.get('project', 'Unknown'),
            symbol=opportunity.get('symbol', 'Unknown'),
            pool_id=opportunity.get('pool', ''),
            initial_investment=investment,
            apy=opportunity.get('apy', 10.0),
            duration_days=duration_days,
            risk_level=opportunity.get('risk_level', 'Medium')
        )

class Portfolio:
    """
    Represents a mock user portfolio with yield farming strategies.
    """
    
    def __init__(self, portfolio_id: str = None, name: str = "My Portfolio"):
        """
        Initialize a portfolio.
        
        Args:
            portfolio_id: Unique ID for the portfolio
            name: Human-readable name for the portfolio
        """
        self.portfolio_id = portfolio_id or f"portfolio-{uuid.uuid4()}"
        self.name = name
        self.strategies = {}  # Map of strategy_id to YieldStrategy
        self.creation_time = datetime.now()
        self.last_update = self.creation_time
    
    def add_strategy(self, strategy: YieldStrategy) -> None:
        """
        Add a strategy to the portfolio.
        
        Args:
            strategy: YieldStrategy to add
        """
        self.strategies[strategy.strategy_id] = strategy
        self.last_update = datetime.now()
    
    def remove_strategy(self, strategy_id: str) -> bool:
        """
        Remove a strategy from the portfolio.
        
        Args:
            strategy_id: ID of the strategy to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if strategy_id in self.strategies:
            del self.strategies[strategy_id]
            self.last_update = datetime.now()
            return True
        return False
    
    def get_total_value(self, day: int = None) -> float:
        """
        Get the total current value of the portfolio.
        
        Args:
            day: Day to calculate value for (None for current)
            
        Returns:
            float: Total portfolio value
        """
        total = 0.0
        
        for strategy in self.strategies.values():
            if day is not None:
                # Get simulated value for specific day
                daily_data = strategy.simulate_daily_returns()
                if day < len(daily_data):
                    total += daily_data[day]["current_value"]
            else:
                # Get current expected value
                returns = strategy.calculate_returns()
                total += returns["compound_final"]
        
        return total
    
    def get_total_investment(self) -> float:
        """Get the total amount invested in the portfolio."""
        return sum(s.initial_investment for s in self.strategies.values())
    
    def get_total_profit(self) -> float:
        """Get the total expected profit of the portfolio."""
        return self.get_total_value() - self.get_total_investment()
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the portfolio.
        
        Returns:
            Dict[str, Any]: Portfolio summary
        """
        total_investment = self.get_total_investment()
        total_value = self.get_total_value()
        total_profit = total_value - total_investment
        
        if total_investment > 0:
            roi = (total_profit / total_investment) * 100
        else:
            roi = 0.0
        
        # Calculate weighted average APY
        if total_investment > 0:
            weighted_apy = sum(s.apy * (s.initial_investment / total_investment) for s in self.strategies.values())
        else:
            weighted_apy = 0.0
        
        # Get protocol distribution
        protocol_distribution = {}
        for strategy in self.strategies.values():
            protocol = strategy.protocol
            if protocol in protocol_distribution:
                protocol_distribution[protocol] += strategy.initial_investment
            else:
                protocol_distribution[protocol] = strategy.initial_investment
        
        return {
            "portfolio_id": self.portfolio_id,
            "name": self.name,
            "creation_time": self.creation_time.isoformat(),
            "last_update": self.last_update.isoformat(),
            "strategy_count": len(self.strategies),
            "total_investment": total_investment,
            "total_value": total_value,
            "total_profit": total_profit,
            "roi": roi,
            "weighted_apy": weighted_apy,
            "protocol_distribution": protocol_distribution
        }
    
    def simulate_portfolio_over_time(self, days: int = 365) -> Dict[str, Any]:
        """
        Simulate the portfolio performance over time.
        
        Args:
            days: Number of days to simulate
            
        Returns:
            Dict[str, Any]: Portfolio performance data
        """
        # Initialize daily totals
        daily_totals = [{"day": day, "total_value": 0.0, "total_profit": 0.0} for day in range(days)]
        
        # Simulate each strategy
        strategy_simulations = {}
        
        for strategy_id, strategy in self.strategies.items():
            simulation_days = min(days, strategy.duration_days)
            daily_data = strategy.simulate_daily_returns()[:simulation_days]
            strategy_simulations[strategy_id] = daily_data
            
            # Add to daily totals
            for day, data in enumerate(daily_data):
                if day < len(daily_totals):
                    daily_totals[day]["total_value"] += data["current_value"]
                    daily_totals[day]["total_profit"] += data["profit"]
        
        # Calculate portfolio ROI for each day
        total_investment = self.get_total_investment()
        for day_data in daily_totals:
            if total_investment > 0:
                day_data["portfolio_roi"] = (day_data["total_profit"] / total_investment) * 100
            else:
                day_data["portfolio_roi"] = 0.0
        
        return {
            "daily_totals": daily_totals,
            "strategy_simulations": strategy_simulations,
            "total_investment": total_investment
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio to dictionary for storage."""
        return {
            "portfolio_id": self.portfolio_id,
            "name": self.name,
            "creation_time": self.creation_time.isoformat(),
            "last_update": self.last_update.isoformat(),
            "strategies": {
                strategy_id: strategy.to_dict()
                for strategy_id, strategy in self.strategies.items()
            },
            "summary": self.get_portfolio_summary()
        }
    
    def save(self) -> str:
        """
        Save the portfolio to disk.
        
        Returns:
            str: Path to saved file
        """
        file_path = PORTFOLIO_DIR / f"{self.portfolio_id}.json"
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        return str(file_path)
    
    @classmethod
    def load(cls, portfolio_id: str) -> 'Portfolio':
        """
        Load a portfolio from disk.
        
        Args:
            portfolio_id: ID of the portfolio to load
            
        Returns:
            Portfolio: Loaded portfolio
        """
        file_path = PORTFOLIO_DIR / f"{portfolio_id}.json"
        
        if not file_path.exists():
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        with open(file_path, "r") as f:
            data = json.load(f)
        
        portfolio = cls(portfolio_id=data["portfolio_id"], name=data["name"])
        
        for strategy_id, strategy_data in data.get("strategies", {}).items():
            strategy = YieldStrategy.from_dict(strategy_data)
            portfolio.strategies[strategy_id] = strategy
        
        # Set timestamps
        if "creation_time" in data:
            portfolio.creation_time = datetime.fromisoformat(data["creation_time"])
        if "last_update" in data:
            portfolio.last_update = datetime.fromisoformat(data["last_update"])
        
        return portfolio
    
    @classmethod
    def list_portfolios(cls) -> List[Dict[str, Any]]:
        """
        List all saved portfolios.
        
        Returns:
            List[Dict[str, Any]]: List of portfolio summaries
        """
        portfolios = []
        
        for file_path in PORTFOLIO_DIR.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                
                portfolios.append({
                    "portfolio_id": data.get("portfolio_id", file_path.stem),
                    "name": data.get("name", "Unnamed Portfolio"),
                    "creation_time": data.get("creation_time", ""),
                    "last_update": data.get("last_update", ""),
                    "strategy_count": len(data.get("strategies", {})),
                    "summary": data.get("summary", {})
                })
            except Exception as e:
                print(f"Error loading portfolio {file_path}: {e}")
        
        return portfolios

class TradeSimulator:
    """
    Simulates yield farming strategies and tracks mock portfolios.
    """
    
    def __init__(self):
        """Initialize the trade simulator."""
        self.active_portfolio = None
        self.default_portfolio_name = "Default Portfolio"
    
    def create_portfolio(self, name: str = "My Portfolio") -> Portfolio:
        """
        Create a new portfolio.
        
        Args:
            name: Portfolio name
            
        Returns:
            Portfolio: New portfolio
        """
        try:
            portfolio = Portfolio(name=name)
            
            # Set as active portfolio
            self.active_portfolio = portfolio
            
            logger.info(f"Created new portfolio: {name}")
            return portfolio
        
        except Exception as e:
            logger.error(f"Error creating portfolio: {e}")
            return None
    
    def load_portfolio(self, portfolio_id: str) -> Portfolio:
        """
        Load a portfolio.
        
        Args:
            portfolio_id: Portfolio ID to load
            
        Returns:
            Portfolio: Loaded portfolio
        """
        try:
            portfolio = Portfolio.load(portfolio_id)
            
            # Set as active portfolio
            self.active_portfolio = portfolio
            
            logger.info(f"Loaded portfolio: {portfolio.name}")
            return portfolio
        
        except Exception as e:
            logger.error(f"Error loading portfolio: {e}")
            return None
    
    def add_strategy_from_opportunity(
        self, 
        opportunity: Dict[str, Any], 
        investment: float = 1000.0, 
        duration_days: int = 365,
        compound_frequency: str = "daily"
    ) -> YieldStrategy:
        """
        Add a strategy to the active portfolio from an opportunity.
        
        Args:
            opportunity: Yield opportunity
            investment: Investment amount
            duration_days: Strategy duration in days
            compound_frequency: Compounding frequency
            
        Returns:
            YieldStrategy: Added strategy
        """
        if not self.active_portfolio:
            logger.warning("No active portfolio. Creating default portfolio.")
            self.create_portfolio(self.default_portfolio_name)
        
        try:
            # Create strategy from opportunity
            strategy = YieldStrategy.from_opportunity(
                opportunity, 
                investment=investment, 
                duration_days=duration_days
            )
            
            # Set compound frequency
            strategy.compound_frequency = compound_frequency
            
            # Add to portfolio
            self.active_portfolio.add_strategy(strategy)
            self.active_portfolio.save()
            
            logger.info(f"Added strategy to portfolio: {strategy.name}")
            return strategy
        
        except Exception as e:
            logger.error(f"Error adding strategy: {e}")
            return None
    
    def create_strategy_from_top_opportunities(
        self, 
        investment_per_strategy: float = 1000.0,
        max_strategies: int = 5,
        duration_days: int = 365,
        min_apy: float = 8.0,
        max_risk_level: str = "Medium"
    ) -> List[YieldStrategy]:
        """
        Automatically create strategies from top opportunities.
        
        Args:
            investment_per_strategy: Amount to invest per strategy
            max_strategies: Maximum number of strategies to create
            duration_days: Strategy duration in days
            min_apy: Minimum APY to consider
            max_risk_level: Maximum risk level to consider
            
        Returns:
            List[YieldStrategy]: Created strategies
        """
        if not self.active_portfolio:
            raise ValueError("No active portfolio. Create or load a portfolio first.")
        
        # Get opportunities
        opportunities = opportunity_detector.get_top_opportunities(top_n=20, force_refresh=False)
        
        # Filter by criteria
        filtered_opps = []
        for opp in opportunities:
            risk_level = opp.get("risk_level", "High")
            apy = opp.get("apy", 0)
            
            risk_levels = ["Low", "Medium", "High", "Very High"]
            max_risk_index = risk_levels.index(max_risk_level)
            
            if apy >= min_apy and risk_levels.index(risk_level) <= max_risk_index:
                filtered_opps.append(opp)
        
        # Limit to max_strategies
        selected_opps = filtered_opps[:max_strategies]
        
        # Create strategies
        strategies = []
        for opp in selected_opps:
            strategy = self.add_strategy_from_opportunity(
                opp,
                investment=investment_per_strategy,
                duration_days=duration_days
            )
            strategies.append(strategy)
        
        return strategies
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """
        Get summary of active portfolio.
        
        Returns:
            Dict[str, Any]: Portfolio summary
        """
        if not self.active_portfolio:
            # Initialize with mock portfolio
            logger.warning("No active portfolio. Creating default portfolio with mock data.")
            self.create_default_mock_portfolio()
            
            if not self.active_portfolio:
                return {
                    "error": "No active portfolio and failed to create mock portfolio."
                }
        
        try:
            return self.active_portfolio.get_portfolio_summary()
        
        except Exception as e:
            logger.error(f"Error getting portfolio summary: {e}")
            return {"error": f"Error getting portfolio summary: {e}"}
    
    def simulate_portfolio_performance(self, days: int = 365) -> Dict[str, Any]:
        """
        Simulate portfolio performance.
        
        Args:
            days: Number of days to simulate
            
        Returns:
            Dict[str, Any]: Simulation results
        """
        if not self.active_portfolio:
            # Initialize with mock portfolio
            logger.warning("No active portfolio. Creating default portfolio with mock data.")
            self.create_default_mock_portfolio()
            
            if not self.active_portfolio:
                return {
                    "error": "No active portfolio and failed to create mock portfolio."
                }
        
        try:
            return self.active_portfolio.simulate_portfolio_over_time(days=days)
        
        except Exception as e:
            logger.error(f"Error simulating portfolio performance: {e}")
            return {"error": f"Error simulating portfolio performance: {e}"}

    def create_default_mock_portfolio(self) -> Portfolio:
        """
        Create a default mock portfolio for demo purposes.
        
        Returns:
            Portfolio: Mock portfolio
        """
        try:
            # Create new portfolio
            portfolio = self.create_portfolio("Demo Portfolio")
            
            # Add mock strategies
            mock_strategies = [
                {
                    "name": "Raydium SOL-USDC LP",
                    "protocol": "Raydium",
                    "symbol": "SOL-USDC",
                    "pool_id": "raydium_sol_usdc_lp",
                    "initial_investment": 1000.0,
                    "apy": 12.5,
                    "risk_level": "Medium"
                },
                {
                    "name": "Marinade Staked SOL",
                    "protocol": "Marinade",
                    "symbol": "mSOL",
                    "pool_id": "marinade_msol",
                    "initial_investment": 500.0,
                    "apy": 6.8,
                    "risk_level": "Low"
                },
                {
                    "name": "Orca ORCA-SOL LP",
                    "protocol": "Orca",
                    "symbol": "ORCA-SOL",
                    "pool_id": "orca_orca_sol_lp",
                    "initial_investment": 750.0,
                    "apy": 18.2,
                    "risk_level": "High"
                }
            ]
            
            # Add each strategy
            for mock_strategy in mock_strategies:
                strategy = YieldStrategy(
                    name=mock_strategy["name"],
                    protocol=mock_strategy["protocol"],
                    symbol=mock_strategy["symbol"],
                    pool_id=mock_strategy["pool_id"],
                    initial_investment=mock_strategy["initial_investment"],
                    apy=mock_strategy["apy"],
                    duration_days=365,
                    compound_frequency="daily",
                    risk_level=mock_strategy["risk_level"]
                )
                portfolio.add_strategy(strategy)
            
            # Save portfolio
            portfolio.save()
            
            logger.info(f"Created default mock portfolio with {len(mock_strategies)} strategies")
            return portfolio
        
        except Exception as e:
            logger.error(f"Error creating default mock portfolio: {e}")
            return None

# Create global instance
trade_simulator = TradeSimulator()

# Create demo portfolio with default strategies
def create_demo_portfolio() -> Portfolio:
    """
    Create a demo portfolio with some strategies.
    
    Returns:
        Portfolio: Demo portfolio
    """
    # Create a fresh portfolio
    portfolio = trade_simulator.create_portfolio("Demo Portfolio")
    
    # Add some sample strategies
    strategies = [
        # Conservative strategy - Marinade staking (lower APY, lower risk)
        YieldStrategy(
            name="Marinade SOL Staking",
            protocol="Marinade",
            symbol="SOL",
            initial_investment=1000.0,
            apy=6.5,
            risk_level="Low"
        ),
        
        # Moderate strategy - Raydium LP (medium APY, medium risk)
        YieldStrategy(
            name="Raydium SOL-USDC LP",
            protocol="Raydium",
            symbol="SOL-USDC",
            initial_investment=2000.0,
            apy=12.0,
            risk_level="Medium"
        ),
        
        # Aggressive strategy - Orca LP (higher APY, higher risk)
        YieldStrategy(
            name="Orca MNDE-SOL LP",
            protocol="Orca",
            symbol="MNDE-SOL",
            initial_investment=500.0,
            apy=24.0,
            risk_level="High"
        )
    ]
    
    for strategy in strategies:
        portfolio.add_strategy(strategy)
    
    # Save the portfolio
    portfolio.save()
    
    return portfolio

if __name__ == "__main__":
    # Create a demo portfolio
    portfolio = create_demo_portfolio()
    
    # Print portfolio summary
    summary = portfolio.get_portfolio_summary()
    
    print("\n=== PORTFOLIO SUMMARY ===")
    print(f"Name: {summary['name']}")
    print(f"Total Investment: ${summary['total_investment']:,.2f}")
    print(f"Expected Value (1yr): ${summary['total_value']:,.2f}")
    print(f"Expected Profit: ${summary['total_profit']:,.2f}")
    print(f"Expected ROI: {summary['roi']:.2f}%")
    print(f"Weighted APY: {summary['weighted_apy']:.2f}%")
    
    # Get daily simulation data
    simulation = portfolio.simulate_portfolio_over_time(days=90)  # 90 day simulation
    
    # Print expected value after specific time periods
    print("\n=== EXPECTED PORTFOLIO VALUE ===")
    print(f"After 30 days: ${simulation['daily_totals'][29]['total_value']:,.2f}")
    print(f"After 60 days: ${simulation['daily_totals'][59]['total_value']:,.2f}")
    print(f"After 90 days: ${simulation['daily_totals'][89]['total_value']:,.2f}")
    
    # Try creating strategies from opportunities
    try:
        print("\n=== CREATING STRATEGIES FROM OPPORTUNITIES ===")
        strategies = trade_simulator.create_strategy_from_top_opportunities(
            investment_per_strategy=1000.0,
            max_strategies=3
        )
        
        print(f"Created {len(strategies)} new strategies from opportunities")
    except Exception as e:
        print(f"Error creating strategies: {e}") 