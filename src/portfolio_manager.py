"""
Portfolio Management Module for HiramAbiff

This module provides functionality for tracking yield strategies and calculating returns.
"""

import os
import json
import datetime
import logging
import uuid
from typing import Dict, List, Any, Optional

from src.blockchain.wallet_integration import wallet_integration
from src.yield_aggregator import YieldAggregator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PortfolioManager:
    """
    Class for managing yield farming portfolios and tracking returns.
    """
    
    def __init__(self, portfolio_dir="portfolios"):
        """
        Initialize the portfolio manager.
        
        Args:
            portfolio_dir: Directory to store portfolios
        """
        self.portfolio_dir = portfolio_dir
        self.yield_aggregator = YieldAggregator()
        os.makedirs(portfolio_dir, exist_ok=True)
        
        # Create active portfolio or load existing
        self.active_portfolio = self._load_active_portfolio()
    
    def _load_active_portfolio(self) -> Dict[str, Any]:
        """
        Load active portfolio or create a new one.
        
        Returns:
            Dict[str, Any]: Active portfolio
        """
        active_portfolio_file = os.path.join(self.portfolio_dir, "active_portfolio.json")
        
        if os.path.exists(active_portfolio_file):
            try:
                with open(active_portfolio_file, "r") as f:
                    logger.info("Loading active portfolio")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading active portfolio: {e}")
                # Create new portfolio if error loading
                return self._create_new_portfolio()
        else:
            # Create new portfolio
            return self._create_new_portfolio()
    
    def _create_new_portfolio(self) -> Dict[str, Any]:
        """
        Create a new portfolio.
        
        Returns:
            Dict[str, Any]: New portfolio
        """
        portfolio = {
            "id": str(uuid.uuid4()),
            "name": "My Yield Portfolio",
            "created_at": datetime.datetime.now().isoformat(),
            "strategies": [],
            "total_invested": 0,
            "total_current_value": 0,
            "total_returns": 0,
            "total_returns_pct": 0,
            "updated_at": datetime.datetime.now().isoformat()
        }
        
        # Save portfolio
        self._save_active_portfolio(portfolio)
        
        return portfolio
    
    def _save_active_portfolio(self, portfolio: Dict[str, Any]) -> None:
        """
        Save active portfolio.
        
        Args:
            portfolio: Portfolio to save
        """
        active_portfolio_file = os.path.join(self.portfolio_dir, "active_portfolio.json")
        
        try:
            with open(active_portfolio_file, "w") as f:
                json.dump(portfolio, f, indent=2)
                logger.info("Saved active portfolio")
        except Exception as e:
            logger.error(f"Error saving active portfolio: {e}")
    
    def get_active_portfolio(self) -> Dict[str, Any]:
        """
        Get active portfolio with updated values.
        
        Returns:
            Dict[str, Any]: Active portfolio
        """
        # Update portfolio values
        self._update_portfolio_values()
        
        return self.active_portfolio
    
    def _update_portfolio_values(self) -> None:
        """
        Update portfolio values based on current yield data.
        """
        # Get latest yield data
        yield_data = self.yield_aggregator.get_data()
        
        total_invested = 0
        total_current_value = 0
        
        # Update strategy values
        for strategy in self.active_portfolio["strategies"]:
            # Find opportunity in yield data
            opportunity_id = strategy.get("opportunity_id")
            opportunity = next((pool for pool in yield_data if pool.get("pool") == opportunity_id), None)
            
            invested_amount = strategy.get("invested_amount", 0)
            total_invested += invested_amount
            
            if opportunity:
                # Update APY
                strategy["current_apy"] = opportunity.get("apy", 0)
                
                # Calculate current value based on time invested and APY
                investment_date = datetime.datetime.fromisoformat(strategy.get("created_at"))
                current_date = datetime.datetime.now()
                days_invested = (current_date - investment_date).days
                
                compound_frequency = strategy.get("compound_frequency", "daily")
                
                if compound_frequency == "daily":
                    compounds_per_year = 365
                elif compound_frequency == "weekly":
                    compounds_per_year = 52
                elif compound_frequency == "monthly":
                    compounds_per_year = 12
                else:  # None/manual
                    compounds_per_year = 1
                
                if compounds_per_year > 0:
                    # Compound interest formula: A = P(1 + r/n)^(nt)
                    # Where:
                    # A = final amount
                    # P = principal
                    # r = annual interest rate (decimal)
                    # n = number of times compounded per year
                    # t = time in years
                    
                    apy_decimal = opportunity.get("apy", 0) / 100
                    time_in_years = days_invested / 365
                    
                    current_value = invested_amount * (1 + apy_decimal / compounds_per_year) ** (compounds_per_year * time_in_years)
                else:
                    # Simple interest
                    apy_decimal = opportunity.get("apy", 0) / 100
                    time_in_years = days_invested / 365
                    
                    current_value = invested_amount * (1 + apy_decimal * time_in_years)
                
                strategy["current_value"] = round(current_value, 2)
                strategy["returns"] = round(current_value - invested_amount, 2)
                strategy["returns_pct"] = round((current_value - invested_amount) / invested_amount * 100, 2) if invested_amount > 0 else 0
                
                # Calculate returns for different time periods
                strategy["daily_returns"] = round(invested_amount * (opportunity.get("apy", 0) / 100 / 365), 2)
                strategy["weekly_returns"] = round(invested_amount * (opportunity.get("apy", 0) / 100 / 52), 2)
                strategy["monthly_returns"] = round(invested_amount * (opportunity.get("apy", 0) / 100 / 12), 2)
                strategy["yearly_returns"] = round(invested_amount * (opportunity.get("apy", 0) / 100), 2)
            else:
                # Opportunity not found, use last known values
                strategy["current_value"] = invested_amount
                strategy["returns"] = 0
                strategy["returns_pct"] = 0
                strategy["daily_returns"] = 0
                strategy["weekly_returns"] = 0
                strategy["monthly_returns"] = 0
                strategy["yearly_returns"] = 0
            
            total_current_value += strategy.get("current_value", 0)
        
        # Update portfolio totals
        self.active_portfolio["total_invested"] = round(total_invested, 2)
        self.active_portfolio["total_current_value"] = round(total_current_value, 2)
        self.active_portfolio["total_returns"] = round(total_current_value - total_invested, 2)
        self.active_portfolio["total_returns_pct"] = round((total_current_value - total_invested) / total_invested * 100, 2) if total_invested > 0 else 0
        self.active_portfolio["updated_at"] = datetime.datetime.now().isoformat()
        
        # Save updated portfolio
        self._save_active_portfolio(self.active_portfolio)
    
    def add_strategy(self, opportunity_id: str, invested_amount: float, duration: int = 365, compound_frequency: str = "daily") -> Dict[str, Any]:
        """
        Add a strategy to the portfolio.
        
        Args:
            opportunity_id: Opportunity ID
            invested_amount: Amount invested
            duration: Investment duration in days
            compound_frequency: Compound frequency (daily, weekly, monthly, None)
            
        Returns:
            Dict[str, Any]: Result
        """
        try:
            # Get opportunity details
            yield_data = self.yield_aggregator.get_data()
            opportunity = next((pool for pool in yield_data if pool.get("pool") == opportunity_id), None)
            
            if not opportunity:
                return {"error": f"Opportunity {opportunity_id} not found"}
            
            # Create strategy
            strategy = {
                "id": str(uuid.uuid4()),
                "opportunity_id": opportunity_id,
                "project": opportunity.get("project", "Unknown"),
                "symbol": opportunity.get("symbol", "Unknown"),
                "chain": opportunity.get("chain", "Unknown"),
                "initial_apy": opportunity.get("apy", 0),
                "current_apy": opportunity.get("apy", 0),
                "risk_level": opportunity.get("risk_level", "Medium"),
                "tvl": opportunity.get("tvlUsd", 0),
                "invested_amount": invested_amount,
                "current_value": invested_amount,
                "returns": 0,
                "returns_pct": 0,
                "daily_returns": round(invested_amount * (opportunity.get("apy", 0) / 100 / 365), 2),
                "weekly_returns": round(invested_amount * (opportunity.get("apy", 0) / 100 / 52), 2),
                "monthly_returns": round(invested_amount * (opportunity.get("apy", 0) / 100 / 12), 2),
                "yearly_returns": round(invested_amount * (opportunity.get("apy", 0) / 100), 2),
                "duration": duration,
                "compound_frequency": compound_frequency,
                "created_at": datetime.datetime.now().isoformat(),
                "end_date": (datetime.datetime.now() + datetime.timedelta(days=duration)).isoformat(),
                "tx_hash": "".join([str(uuid.uuid4().hex)[:16] for _ in range(4)])  # Mock transaction hash
            }
            
            # Add strategy to portfolio
            self.active_portfolio["strategies"].append(strategy)
            
            # Update portfolio values
            self._update_portfolio_values()
            
            # Create mock transaction if wallet connected
            wallet_data = wallet_integration.get_wallet_data()
            if "error" not in wallet_data:
                wallet_integration.create_transaction(
                    tx_type="deposit",
                    protocol=opportunity.get("project", "Unknown"),
                    asset=opportunity.get("symbol", "Unknown"),
                    amount=invested_amount
                )
            
            return {
                "success": True,
                "message": f"Added strategy for {opportunity.get('symbol', 'Unknown')} on {opportunity.get('project', 'Unknown')}",
                "strategy": strategy
            }
        
        except Exception as e:
            logger.error(f"Error adding strategy: {e}")
            return {"error": f"Error adding strategy: {e}"}
    
    def remove_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Remove a strategy from the portfolio.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Dict[str, Any]: Result
        """
        try:
            # Find strategy
            strategy = next((s for s in self.active_portfolio["strategies"] if s.get("id") == strategy_id), None)
            
            if not strategy:
                return {"error": f"Strategy {strategy_id} not found"}
            
            # Remove strategy
            self.active_portfolio["strategies"] = [s for s in self.active_portfolio["strategies"] if s.get("id") != strategy_id]
            
            # Update portfolio values
            self._update_portfolio_values()
            
            # Create mock transaction if wallet connected
            wallet_data = wallet_integration.get_wallet_data()
            if "error" not in wallet_data:
                wallet_integration.create_transaction(
                    tx_type="withdraw",
                    protocol=strategy.get("project", "Unknown"),
                    asset=strategy.get("symbol", "Unknown"),
                    amount=strategy.get("current_value", 0)
                )
            
            return {
                "success": True,
                "message": f"Removed strategy for {strategy.get('symbol', 'Unknown')} on {strategy.get('project', 'Unknown')}",
                "removed_strategy": strategy
            }
        
        except Exception as e:
            logger.error(f"Error removing strategy: {e}")
            return {"error": f"Error removing strategy: {e}"}
    
    def get_strategy(self, strategy_id: str) -> Dict[str, Any]:
        """
        Get a strategy from the portfolio.
        
        Args:
            strategy_id: Strategy ID
            
        Returns:
            Dict[str, Any]: Strategy or error
        """
        try:
            # Find strategy
            strategy = next((s for s in self.active_portfolio["strategies"] if s.get("id") == strategy_id), None)
            
            if not strategy:
                return {"error": f"Strategy {strategy_id} not found"}
            
            return strategy
        
        except Exception as e:
            logger.error(f"Error getting strategy: {e}")
            return {"error": f"Error getting strategy: {e}"}
    
    def calculate_portfolio_risk(self) -> Dict[str, Any]:
        """
        Calculate portfolio risk metrics.
        
        Returns:
            Dict[str, Any]: Risk metrics
        """
        try:
            if not self.active_portfolio["strategies"]:
                return {
                    "avg_risk_score": 0,
                    "risk_level": "None",
                    "risk_distribution": {},
                    "chain_distribution": {},
                    "project_distribution": {}
                }
            
            # Calculate weighted average risk score
            total_invested = self.active_portfolio["total_invested"]
            risk_score_sum = 0
            
            risk_distribution = {}
            chain_distribution = {}
            project_distribution = {}
            
            for strategy in self.active_portfolio["strategies"]:
                weight = strategy.get("invested_amount", 0) / total_invested if total_invested > 0 else 0
                
                # Use risk level to derive risk score
                risk_level = strategy.get("risk_level", "Medium")
                risk_score = 5  # Default medium
                
                if risk_level == "Very Low":
                    risk_score = 1
                elif risk_level == "Low":
                    risk_score = 3
                elif risk_level == "Medium":
                    risk_score = 5
                elif risk_level == "High":
                    risk_score = 7
                elif risk_level == "Very High":
                    risk_score = 9
                
                risk_score_sum += risk_score * weight
                
                # Update distributions
                if risk_level in risk_distribution:
                    risk_distribution[risk_level] += weight
                else:
                    risk_distribution[risk_level] = weight
                
                chain = strategy.get("chain", "Unknown")
                if chain in chain_distribution:
                    chain_distribution[chain] += weight
                else:
                    chain_distribution[chain] = weight
                
                project = strategy.get("project", "Unknown")
                if project in project_distribution:
                    project_distribution[project] += weight
                else:
                    project_distribution[project] = weight
            
            # Convert weights to percentages
            for key in risk_distribution:
                risk_distribution[key] = round(risk_distribution[key] * 100, 2)
                
            for key in chain_distribution:
                chain_distribution[key] = round(chain_distribution[key] * 100, 2)
                
            for key in project_distribution:
                project_distribution[key] = round(project_distribution[key] * 100, 2)
            
            # Determine overall risk level
            avg_risk_score = risk_score_sum
            risk_level = "Medium"  # Default
            
            if avg_risk_score < 2.5:
                risk_level = "Very Low"
            elif avg_risk_score < 4:
                risk_level = "Low"
            elif avg_risk_score < 6:
                risk_level = "Medium"
            elif avg_risk_score < 8:
                risk_level = "High"
            else:
                risk_level = "Very High"
            
            return {
                "avg_risk_score": round(avg_risk_score, 2),
                "risk_level": risk_level,
                "risk_distribution": risk_distribution,
                "chain_distribution": chain_distribution,
                "project_distribution": project_distribution
            }
        
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return {"error": f"Error calculating portfolio risk: {e}"}
    
    def simulate_portfolio_returns(self, duration_days: int = 365) -> Dict[str, Any]:
        """
        Simulate portfolio returns over time.
        
        Args:
            duration_days: Simulation duration in days
            
        Returns:
            Dict[str, Any]: Simulated returns
        """
        try:
            if not self.active_portfolio["strategies"]:
                return {
                    "error": "No strategies in portfolio"
                }
            
            # Get current portfolio state
            current_value = self.active_portfolio["total_current_value"]
            current_apy_weighted = 0
            
            # Calculate weighted average APY
            for strategy in self.active_portfolio["strategies"]:
                weight = strategy.get("current_value", 0) / current_value if current_value > 0 else 0
                current_apy_weighted += strategy.get("current_apy", 0) * weight
            
            # Generate projection points (monthly)
            projection = []
            months = duration_days // 30
            
            for month in range(months + 1):
                days = month * 30
                time_in_years = days / 365
                
                # Compound interest formula: A = P(1 + r/n)^(nt)
                projected_value = current_value * (1 + current_apy_weighted / 100 / 12) ** (month)
                
                projection.append({
                    "month": month,
                    "days": days,
                    "value": round(projected_value, 2),
                    "growth": round(projected_value - current_value, 2),
                    "growth_pct": round((projected_value - current_value) / current_value * 100, 2) if current_value > 0 else 0
                })
            
            return {
                "initial_value": current_value,
                "current_apy_weighted": round(current_apy_weighted, 2),
                "final_value": projection[-1]["value"],
                "total_growth": projection[-1]["growth"],
                "total_growth_pct": projection[-1]["growth_pct"],
                "projection": projection
            }
        
        except Exception as e:
            logger.error(f"Error simulating portfolio returns: {e}")
            return {"error": f"Error simulating portfolio returns: {e}"}
    
    def create_optimization_suggestion(self) -> Dict[str, Any]:
        """
        Create portfolio optimization suggestions.
        
        Returns:
            Dict[str, Any]: Optimization suggestions
        """
        try:
            if not self.active_portfolio["strategies"]:
                return {
                    "error": "No strategies in portfolio to optimize"
                }
            
            # Get latest yield data
            yield_data = self.yield_aggregator.get_data()
            
            # Get current portfolio state
            strategies = self.active_portfolio["strategies"]
            total_value = self.active_portfolio["total_current_value"]
            current_apy_weighted = 0
            
            # Calculate weighted average APY
            for strategy in strategies:
                weight = strategy.get("current_value", 0) / total_value if total_value > 0 else 0
                current_apy_weighted += strategy.get("current_apy", 0) * weight
            
            # Find better opportunities
            suggestions = []
            
            for strategy in strategies:
                current_chain = strategy.get("chain", "Unknown")
                current_project = strategy.get("project", "Unknown")
                current_apy = strategy.get("current_apy", 0)
                risk_level = strategy.get("risk_level", "Medium")
                
                # Convert risk level to max risk score
                max_risk = 10
                
                if risk_level == "Very Low":
                    max_risk = 3
                elif risk_level == "Low":
                    max_risk = 5
                elif risk_level == "Medium":
                    max_risk = 7
                elif risk_level == "High":
                    max_risk = 9
                
                # Find better opportunities with similar risk profile
                better_opportunities = []
                
                # First, look in same chain
                for pool in yield_data:
                    if pool.get("chain") == current_chain and pool.get("apy", 0) > current_apy * 1.2 and pool.get("risk_score", 10) <= max_risk:
                        better_opportunities.append(pool)
                
                # Then, look in other chains with higher returns
                if len(better_opportunities) < 3:
                    for pool in yield_data:
                        if pool.get("chain") != current_chain and pool.get("apy", 0) > current_apy * 1.5 and pool.get("risk_score", 10) <= max_risk:
                            better_opportunities.append(pool)
                
                # Sort by APY (highest first)
                better_opportunities.sort(key=lambda x: x.get("apy", 0), reverse=True)
                
                # Take top 3 opportunities
                better_opportunities = better_opportunities[:3]
                
                if better_opportunities:
                    suggestions.append({
                        "strategy_id": strategy.get("id"),
                        "current_strategy": {
                            "project": current_project,
                            "chain": current_chain,
                            "symbol": strategy.get("symbol", "Unknown"),
                            "apy": current_apy,
                            "risk_level": risk_level
                        },
                        "better_opportunities": [
                            {
                                "project": op.get("project", "Unknown"),
                                "chain": op.get("chain", "Unknown"),
                                "symbol": op.get("symbol", "Unknown"),
                                "apy": op.get("apy", 0),
                                "risk_level": op.get("risk_level", "Medium"),
                                "apy_difference": round(op.get("apy", 0) - current_apy, 2),
                                "potential_yearly_gain": round(strategy.get("invested_amount", 0) * (op.get("apy", 0) - current_apy) / 100, 2)
                            }
                            for op in better_opportunities
                        ]
                    })
            
            # Calculate total potential gain from all suggestions
            total_potential_gain = 0
            
            for suggestion in suggestions:
                if suggestion["better_opportunities"]:
                    # Use the first (best) opportunity
                    total_potential_gain += suggestion["better_opportunities"][0]["potential_yearly_gain"]
            
            return {
                "current_apy_weighted": round(current_apy_weighted, 2),
                "suggestions": suggestions,
                "total_potential_gain": round(total_potential_gain, 2),
                "potential_apy_increase": round(total_potential_gain / total_value * 100, 2) if total_value > 0 else 0
            }
        
        except Exception as e:
            logger.error(f"Error creating optimization suggestions: {e}")
            return {"error": f"Error creating optimization suggestions: {e}"}

# Create singleton instance
portfolio_manager = PortfolioManager() 