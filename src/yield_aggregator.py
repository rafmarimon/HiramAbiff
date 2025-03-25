import os
import time
import json
import requests
import math
import random
import datetime
import logging

class YieldAggregator:
    """A class that aggregates yield data from DeFi Llama API."""

    def __init__(self, cache_dir="cache"):
        """Initialize the YieldAggregator."""
        self.base_url = "https://yields.llama.fi"
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "yield_data.json")
        self.cache_expires = 3600  # 1 hour
        
        # Risk scoring weights
        self.risk_weights = {
            "tvl": 0.3,           # Higher TVL = lower risk
            "apy_volatility": 0.2, # Higher volatility = higher risk
            "protocol_age": 0.15,  # Newer protocols = higher risk
            "audits": 0.2,         # More audits = lower risk
            "chain": 0.15          # Chain reputation score
        }
        
        # Chain risk scores (lower = less risky)
        self.chain_risk = {
            "Ethereum": 1.0,
            "Polygon": 1.5,
            "Arbitrum": 1.8,
            "Optimism": 1.8,
            "Avalanche": 2.0,
            "Fantom": 2.5,
            "Solana": 2.2,
            "BSC": 2.3,
            "Tron": 3.0,
            "Harmony": 3.5
        }
        
        # Default chain risk for unlisted chains
        self.default_chain_risk = 3.0
        
        # Protocol age data (mock data - in production, this would be from an API)
        self.protocol_age = {
            "Aave": 3.5,       # Years since launch
            "Compound": 4.0,
            "Curve": 3.0,
            "Uniswap": 4.0,
            "SushiSwap": 2.5,
            "PancakeSwap": 2.5,
            "Raydium": 1.5,
            "Orca": 1.5,
            "Marinade": 1.0
        }
        self.default_protocol_age = 1.0
        
        # Protocol audit data (mock data - in production, this would be from an API)
        self.protocol_audits = {
            "Aave": 5,        # Number of reputable audits
            "Compound": 4,
            "Curve": 3,
            "Uniswap": 4,
            "SushiSwap": 3,
            "PancakeSwap": 3,
            "Raydium": 2,
            "Orca": 2,
            "Marinade": 2
        }
        self.default_protocol_audits = 1

    def get_data(self, refresh=False):
        """
        Get yield data from DeFi Llama API or cache.
        
        Args:
            refresh (bool): Whether to refresh cache
            
        Returns:
            list: Yield data
        """
        if not refresh and os.path.exists(self.cache_file):
            # Check if cache is still valid
            modified_time = os.path.getmtime(self.cache_file)
            if time.time() - modified_time < self.cache_expires:
                with open(self.cache_file, "r") as f:
                    logging.info("Using cached yield data")
                    return json.load(f)
        
        # Cache expired or doesn't exist, fetch new data
        try:
            logging.info("Fetching yield data from DeFi Llama API")
            response = requests.get(f"{self.base_url}/pools")
            response.raise_for_status()
            data = response.json()
            
            # Add risk assessment
            for pool in data:
                pool["risk_score"] = self._calculate_risk_score(pool)
                pool["risk_level"] = self._risk_score_to_level(pool["risk_score"])
                
                # Add user-friendly description
                pool["description"] = self._generate_description(pool)
                
                # Add historical APY trend (mock data)
                pool["apy_history"] = self._generate_apy_history(pool)
                
                # Add expected returns for common investment amounts
                pool["expected_returns"] = self._calculate_expected_returns(pool)
            
            # Save to cache
            with open(self.cache_file, "w") as f:
                json.dump(data, f)
            
            return data
        except Exception as e:
            logging.error(f"Error fetching yield data: {e}")
            # If cache exists but is expired, use it as fallback
            if os.path.exists(self.cache_file):
                with open(self.cache_file, "r") as f:
                    logging.info("Using expired cached yield data as fallback")
                    return json.load(f)
            raise

    def _calculate_risk_score(self, pool):
        """
        Calculate risk score for a pool (1-10, where 10 is highest risk)
        
        Args:
            pool (dict): Pool data
            
        Returns:
            float: Risk score
        """
        # TVL risk component: Higher TVL = lower risk
        tvl = pool.get("tvlUsd", 0)
        tvl_risk = 10 if tvl == 0 else max(1, min(10, 10 * (1 - math.log10(tvl) / 10)))
        
        # APY volatility (use difference between base APY and 7d average as proxy)
        apy_base = pool.get("apyBase", 0) or 0
        apy_7d = pool.get("apyBase7d", 0) or 0
        apy_volatility = min(10, abs(apy_base - apy_7d) * 2)
        
        # Protocol age
        protocol = pool.get("project", "")
        protocol_age_years = self.protocol_age.get(protocol, self.default_protocol_age)
        protocol_age_risk = max(1, min(10, 10 / (protocol_age_years + 1)))
        
        # Audit count
        audit_count = self.protocol_audits.get(protocol, self.default_protocol_audits)
        audit_risk = max(1, min(10, 10 / (audit_count + 1)))
        
        # Chain risk
        chain = pool.get("chain", "")
        chain_risk_score = self.chain_risk.get(chain, self.default_chain_risk)
        
        # Calculate weighted average
        risk_score = (
            tvl_risk * self.risk_weights["tvl"] +
            apy_volatility * self.risk_weights["apy_volatility"] +
            protocol_age_risk * self.risk_weights["protocol_age"] +
            audit_risk * self.risk_weights["audits"] +
            chain_risk_score * self.risk_weights["chain"]
        )
        
        return round(risk_score, 1)

    def _risk_score_to_level(self, score):
        """
        Convert risk score to user-friendly risk level
        
        Args:
            score (float): Risk score (1-10)
            
        Returns:
            str: Risk level
        """
        if score < 2.5:
            return "Very Low"
        elif score < 4:
            return "Low"
        elif score < 6:
            return "Medium"
        elif score < 8:
            return "High"
        else:
            return "Very High"

    def _generate_description(self, pool):
        """
        Generate user-friendly description for pool
        
        Args:
            pool (dict): Pool data
            
        Returns:
            str: Description
        """
        project = pool.get("project", "Unknown")
        chain = pool.get("chain", "Unknown")
        symbol = pool.get("symbol", "Unknown")
        apy = pool.get("apy", 0)
        
        if "lp" in pool.get("poolMeta", "").lower() or "lp" in symbol.lower():
            return f"Liquidity pool on {project} ({chain}) offering {apy:.2f}% APY for providing liquidity with {symbol}"
        elif "lending" in pool.get("project", "").lower():
            return f"Lending opportunity on {project} ({chain}) offering {apy:.2f}% APY for lending {symbol}"
        elif "staking" in pool.get("project", "").lower() or "stake" in pool.get("poolMeta", "").lower():
            return f"Staking pool on {project} ({chain}) offering {apy:.2f}% APY for staking {symbol}"
        else:
            return f"Yield opportunity on {project} ({chain}) offering {apy:.2f}% APY for {symbol}"

    def _generate_apy_history(self, pool):
        """
        Generate mock APY history data
        
        Args:
            pool (dict): Pool data
            
        Returns:
            list: APY history
        """
        current_apy = pool.get("apy", 0)
        base_apy_7d = pool.get("apyBase7d", current_apy * 0.9)
        
        # Generate 30 days of APY history
        history = []
        for i in range(30, 0, -1):
            # Create realistic, slightly volatile APY history
            day_factor = 1 + (math.sin(i / 5) * 0.1)
            volatility = random.uniform(0.95, 1.05)
            
            if i > 21:  # Older data (22-30 days ago)
                apy = base_apy_7d * day_factor * volatility
            else:  # Newer data (1-21 days ago)
                # Gradually transition from 7d APY to current APY
                transition_factor = i / 21
                apy = (base_apy_7d * transition_factor + current_apy * (1 - transition_factor)) * day_factor * volatility
            
            date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
            history.append({"date": date, "apy": round(apy, 2)})
        
        return history

    def _calculate_expected_returns(self, pool):
        """
        Calculate expected returns for common investment amounts
        
        Args:
            pool (dict): Pool data
            
        Returns:
            dict: Expected returns
        """
        apy = pool.get("apy", 0)
        
        # Common investment amounts
        amounts = [100, 1000, 10000, 100000]
        returns = {}
        
        for amount in amounts:
            # Calculate returns for different time periods
            daily = amount * (apy / 100 / 365)
            weekly = amount * (apy / 100 / 52)
            monthly = amount * (apy / 100 / 12)
            yearly = amount * (apy / 100)
            
            # Calculate compounded returns (yearly)
            compounded = amount * ((1 + (apy / 100 / 365)) ** 365 - 1)
            
            returns[str(amount)] = {
                "daily": round(daily, 2),
                "weekly": round(weekly, 2),
                "monthly": round(monthly, 2),
                "yearly": round(yearly, 2),
                "yearly_compounded": round(compounded, 2)
            }
        
        return returns

    def get_pools_by_chain(self, chain, min_tvl=0, min_apy=0, max_risk=10, limit=50):
        """
        Get pools filtered by chain and other criteria
        
        Args:
            chain (str): Chain name
            min_tvl (float): Minimum TVL in USD
            min_apy (float): Minimum APY
            max_risk (float): Maximum risk score (1-10)
            limit (int): Maximum number of results
            
        Returns:
            list: Filtered pools
        """
        data = self.get_data()
        
        filtered = [
            pool for pool in data 
            if pool.get("chain") == chain
            and pool.get("tvlUsd", 0) >= min_tvl
            and pool.get("apy", 0) >= min_apy
            and pool.get("risk_score", 10) <= max_risk
        ]
        
        # Sort by APY (highest first)
        filtered.sort(key=lambda x: x.get("apy", 0), reverse=True)
        
        return filtered[:limit]

    def get_pools_by_project(self, project, min_tvl=0, min_apy=0, max_risk=10, limit=50):
        """
        Get pools filtered by project and other criteria
        
        Args:
            project (str): Project name
            min_tvl (float): Minimum TVL in USD
            min_apy (float): Minimum APY
            max_risk (float): Maximum risk score (1-10)
            limit (int): Maximum number of results
            
        Returns:
            list: Filtered pools
        """
        data = self.get_data()
        
        filtered = [
            pool for pool in data 
            if pool.get("project") == project
            and pool.get("tvlUsd", 0) >= min_tvl
            and pool.get("apy", 0) >= min_apy
            and pool.get("risk_score", 10) <= max_risk
        ]
        
        # Sort by APY (highest first)
        filtered.sort(key=lambda x: x.get("apy", 0), reverse=True)
        
        return filtered[:limit]

    def get_best_opportunities(self, min_tvl=100000, min_apy=0, max_risk=6, limit=20):
        """
        Get best yield opportunities across all chains
        
        Args:
            min_tvl (float): Minimum TVL in USD
            min_apy (float): Minimum APY
            max_risk (float): Maximum risk score (1-10)
            limit (int): Maximum number of results
            
        Returns:
            list: Best opportunities
        """
        data = self.get_data()
        
        filtered = [
            pool for pool in data 
            if pool.get("tvlUsd", 0) >= min_tvl
            and pool.get("apy", 0) >= min_apy
            and pool.get("risk_score", 10) <= max_risk
        ]
        
        # Sort by APY (highest first)
        filtered.sort(key=lambda x: x.get("apy", 0), reverse=True)
        
        return filtered[:limit]

    def get_safe_opportunities(self, min_tvl=1000000, max_risk=3, min_apy=0, limit=20):
        """
        Get safe yield opportunities (low risk)
        
        Args:
            min_tvl (float): Minimum TVL in USD
            max_risk (float): Maximum risk score (1-10)
            min_apy (float): Minimum APY
            limit (int): Maximum number of results
            
        Returns:
            list: Safe opportunities
        """
        data = self.get_data()
        
        filtered = [
            pool for pool in data 
            if pool.get("tvlUsd", 0) >= min_tvl
            and pool.get("risk_score", 10) <= max_risk
            and pool.get("apy", 0) >= min_apy
        ]
        
        # Sort by APY (highest first)
        filtered.sort(key=lambda x: x.get("apy", 0), reverse=True)
        
        return filtered[:limit]

    def get_stats_by_chain(self):
        """
        Get yield statistics aggregated by chain
        
        Returns:
            dict: Chain statistics
        """
        data = self.get_data()
        
        stats = {}
        
        # Group by chain
        for pool in data:
            chain = pool.get("chain")
            if not chain:
                continue
                
            if chain not in stats:
                stats[chain] = {
                    "count": 0,
                    "total_tvl": 0,
                    "avg_apy": 0,
                    "max_apy": 0,
                    "min_apy": float('inf'),
                    "avg_risk": 0,
                    "pools": []
                }
            
            stats[chain]["count"] += 1
            stats[chain]["total_tvl"] += pool.get("tvlUsd", 0)
            stats[chain]["avg_apy"] += pool.get("apy", 0)
            stats[chain]["max_apy"] = max(stats[chain]["max_apy"], pool.get("apy", 0))
            stats[chain]["min_apy"] = min(stats[chain]["min_apy"], pool.get("apy", 0) or float('inf'))
            stats[chain]["avg_risk"] += pool.get("risk_score", 5)
            stats[chain]["pools"].append(pool)
        
        # Calculate averages
        for chain in stats:
            count = stats[chain]["count"]
            if count > 0:
                stats[chain]["avg_apy"] = stats[chain]["avg_apy"] / count
                stats[chain]["avg_risk"] = stats[chain]["avg_risk"] / count
            
            if stats[chain]["min_apy"] == float('inf'):
                stats[chain]["min_apy"] = 0
        
        return stats

    def get_stats_by_project(self):
        """
        Get yield statistics aggregated by project
        
        Returns:
            dict: Project statistics
        """
        data = self.get_data()
        
        stats = {}
        
        # Group by project
        for pool in data:
            project = pool.get("project")
            if not project:
                continue
                
            if project not in stats:
                stats[project] = {
                    "count": 0,
                    "total_tvl": 0,
                    "avg_apy": 0,
                    "max_apy": 0,
                    "min_apy": float('inf'),
                    "avg_risk": 0,
                    "chains": set(),
                    "pools": []
                }
            
            stats[project]["count"] += 1
            stats[project]["total_tvl"] += pool.get("tvlUsd", 0)
            stats[project]["avg_apy"] += pool.get("apy", 0)
            stats[project]["max_apy"] = max(stats[project]["max_apy"], pool.get("apy", 0))
            stats[project]["min_apy"] = min(stats[project]["min_apy"], pool.get("apy", 0) or float('inf'))
            stats[project]["avg_risk"] += pool.get("risk_score", 5)
            stats[project]["chains"].add(pool.get("chain", "Unknown"))
            stats[project]["pools"].append(pool)
        
        # Calculate averages
        for project in stats:
            count = stats[project]["count"]
            if count > 0:
                stats[project]["avg_apy"] = stats[project]["avg_apy"] / count
                stats[project]["avg_risk"] = stats[project]["avg_risk"] / count
            
            if stats[project]["min_apy"] == float('inf'):
                stats[project]["min_apy"] = 0
                
            # Convert set to list for JSON serialization
            stats[project]["chains"] = list(stats[project]["chains"])
        
        return stats 