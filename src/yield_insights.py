#!/usr/bin/env python
"""
Yield Insights for HiramAbiff

This module provides LLM-powered analysis of yield opportunities using
OpenAI's API, with cost-efficient prompts and caching to minimize API calls.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache directory setup
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

# Function to read API key from environment
def get_openai_api_key() -> Optional[str]:
    """
    Get OpenAI API key from environment or .env file.
    
    Returns:
        Optional[str]: API key or None if not found
    """
    # Try to load directly from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    # If not found, try to load from .env file
    if not api_key:
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.environ.get("OPENAI_API_KEY")
        except ImportError:
            logger.warning("python-dotenv not installed, can't load from .env file")
    
    return api_key

class YieldInsights:
    """
    Provides AI-powered insights for yield farming opportunities.
    """
    
    def __init__(self, cache_ttl: int = 3600 * 8):  # Default 8 hour cache
        """
        Initialize the yield insights module.
        
        Args:
            cache_ttl: Time-to-live for cached insights in seconds
        """
        self.cache_ttl = cache_ttl
        self.api_key = get_openai_api_key()
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. LLM insights will not be available.")
    
    def _get_cache_key(self, prompt_type: str, data_hash: str) -> str:
        """Generate a cache key based on prompt type and data hash."""
        return f"insight_{prompt_type}_{data_hash}"
    
    def _get_cache_path(self, key: str) -> Path:
        """Get path to cache file for a key."""
        # Create a safe filename from the key
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return CACHE_DIR / f"{safe_key}.json"
    
    def _load_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load insights from cache if available and not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Optional[Dict[str, Any]]: Cached data or None
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is expired
            mtime = cache_path.stat().st_mtime
            if time.time() - mtime > self.cache_ttl:
                logger.info(f"Cache expired for {key}")
                return None
            
            # Load cache
            with open(cache_path, "r") as f:
                data = json.load(f)
                logger.info(f"Loaded insights from cache: {key}")
                return data
        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None
    
    def _save_to_cache(self, key: str, data: Dict[str, Any]) -> None:
        """
        Save insights to cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, "w") as f:
                json.dump(data, f, indent=2)
                logger.info(f"Saved insights to cache: {key}")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def _generate_data_hash(self, data: Any) -> str:
        """
        Generate a simple hash for data to use in cache keys.
        
        Args:
            data: Data to hash
            
        Returns:
            str: Hash string
        """
        import hashlib
        
        if isinstance(data, list):
            # For lists (like opportunities), hash based on relevant fields
            hash_content = []
            for item in data:
                if isinstance(item, dict):
                    key_parts = []
                    for k in ["project", "symbol", "apy", "tvlUsd"]:
                        if k in item:
                            key_parts.append(f"{k}:{item[k]}")
                    hash_content.append(",".join(key_parts))
            content_str = "|".join(hash_content)
        elif isinstance(data, dict):
            # For single opportunity
            content_str = "|".join(f"{k}:{v}" for k, v in data.items() 
                                if k in ["project", "symbol", "apy", "tvlUsd"])
        else:
            # Fallback
            content_str = str(data)
        
        # Create MD5 hash
        return hashlib.md5(content_str.encode()).hexdigest()
    
    def generate_yield_summary(self, opportunities: List[Dict[str, Any]], force_refresh: bool = False) -> Dict[str, Any]:
        """
        Generate a summary of yield opportunities using OpenAI API.
        
        Args:
            opportunities: List of yield opportunities
            force_refresh: Whether to force refresh cached insights
            
        Returns:
            Dict[str, Any]: Generated insights
        """
        if not opportunities:
            return {
                "error": "No opportunities provided",
                "timestamp": datetime.now().isoformat()
            }
        
        # Generate data hash for cache key
        data_hash = self._generate_data_hash(opportunities)
        cache_key = self._get_cache_key("yield_summary", data_hash)
        
        # Try to load from cache
        if not force_refresh:
            cached_insights = self._load_from_cache(cache_key)
            if cached_insights:
                return cached_insights
        
        # If no API key, return a placeholder
        if not self.api_key:
            return {
                "summary": "OpenAI API key not configured. Please add your API key to use AI-powered insights.",
                "error": "API key not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Format opportunities data for the prompt
        # Only include necessary information to keep costs down
        formatted_opps = []
        
        for i, opp in enumerate(opportunities[:10]):  # Limit to top 10
            apy = opp.get("apy", 0)
            tvl = opp.get("tvlUsd", 0)
            project = opp.get("project", "Unknown")
            symbol = opp.get("symbol", "Unknown")
            risk_level = opp.get("risk_level", "Unknown")
            
            formatted_opps.append(
                f"{i+1}. {project} - {symbol}: {apy:.2f}% APY, ${tvl:,.2f} TVL, Risk: {risk_level}"
            )
        
        opportunities_text = "\n".join(formatted_opps)
        
        # Add some aggregated stats
        avg_apy = sum(opp.get("apy", 0) for opp in opportunities) / max(1, len(opportunities))
        total_tvl = sum(opp.get("tvlUsd", 0) for opp in opportunities)
        risk_distribution = {}
        
        for opp in opportunities:
            risk = opp.get("risk_level", "Unknown")
            if risk in risk_distribution:
                risk_distribution[risk] += 1
            else:
                risk_distribution[risk] = 1
        
        stats_text = f"""
Average APY: {avg_apy:.2f}%
Total TVL: ${total_tvl:,.2f}
Risk Distribution: {', '.join(f"{risk}: {count}" for risk, count in risk_distribution.items())}
"""
        
        # Create a concise prompt for the API
        prompt = f"""Analyze these top yield farming opportunities:

{opportunities_text}

Additional Stats:
{stats_text}

Provide a concise analysis including:
1. Overall market assessment (2-3 sentences)
2. Best opportunities by risk level (2-3 bullet points)
3. One notable trend or observation
4. One cautionary note

Keep the total response under 250 words.
"""
        
        try:
            # Import here to avoid requiring OpenAI package if not used
            import openai
            
            # Create client
            client = openai.OpenAI(api_key=self.api_key)
            
            # Make API call with cost-effective model
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use the cheapest model that works well
                messages=[
                    {"role": "system", "content": "You are an expert in DeFi yield analysis. Provide concise, valuable insights for yield farmers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,  # Limit token usage
                temperature=0.7
            )
            
            # Extract content
            analysis = response.choices[0].message.content.strip()
            
            # Prepare result
            result = {
                "summary": analysis,
                "opportunities_analyzed": len(opportunities),
                "timestamp": datetime.now().isoformat(),
                "stats": {
                    "avg_apy": avg_apy,
                    "total_tvl": total_tvl,
                    "risk_distribution": risk_distribution
                }
            }
            
            # Cache the result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            
            # Return error info
            return {
                "error": str(e),
                "summary": f"Error generating insights: {str(e)}. Please check your API key and try again.",
                "timestamp": datetime.now().isoformat()
            }
    
    def analyze_portfolio(self, portfolio_data: Dict[str, Any], force_refresh: bool = False) -> Dict[str, Any]:
        """
        Generate insights for a portfolio.
        
        Args:
            portfolio_data: Portfolio data
            force_refresh: Whether to force refresh cached insights
            
        Returns:
            Dict[str, Any]: Generated insights
        """
        if not portfolio_data:
            return {
                "error": "No portfolio data provided",
                "timestamp": datetime.now().isoformat()
            }
        
        # Generate data hash for cache key
        data_hash = self._generate_data_hash(portfolio_data)
        cache_key = self._get_cache_key("portfolio_analysis", data_hash)
        
        # Try to load from cache
        if not force_refresh:
            cached_insights = self._load_from_cache(cache_key)
            if cached_insights:
                return cached_insights
        
        # If no API key, return a placeholder
        if not self.api_key:
            return {
                "summary": "OpenAI API key not configured. Please add your API key to use AI-powered insights.",
                "error": "API key not found",
                "timestamp": datetime.now().isoformat()
            }
        
        # Extract portfolio summary
        summary = portfolio_data.get("summary", {})
        strategies = portfolio_data.get("strategies", {})
        
        # Format portfolio data for the prompt
        strategies_text = []
        
        for strategy_id, strategy in strategies.items():
            name = strategy.get("name", "Unknown Strategy")
            protocol = strategy.get("protocol", "Unknown")
            symbol = strategy.get("symbol", "Unknown")
            investment = strategy.get("initial_investment", 0)
            apy = strategy.get("apy", 0)
            risk_level = strategy.get("risk_level", "Unknown")
            expected_returns = strategy.get("expected_returns", {})
            
            compound_roi = expected_returns.get("compound_roi", 0)
            compound_final = expected_returns.get("compound_final", 0)
            
            strategies_text.append(
                f"{protocol} - {symbol}: ${investment:,.2f} invested, {apy:.2f}% APY, Risk: {risk_level}, "
                f"Expected ROI: {compound_roi:.2f}%, Final Value: ${compound_final:,.2f}"
            )
        
        portfolio_text = "\n".join(strategies_text)
        
        # Add overall portfolio stats
        total_investment = summary.get("total_investment", 0)
        total_value = summary.get("total_value", 0)
        roi = summary.get("roi", 0)
        weighted_apy = summary.get("weighted_apy", 0)
        
        stats_text = f"""
Total Investment: ${total_investment:,.2f}
Expected Final Value: ${total_value:,.2f}
Expected ROI: {roi:.2f}%
Weighted APY: {weighted_apy:.2f}%
"""
        
        # Create a concise prompt for the API
        prompt = f"""Analyze this yield farming portfolio:

Portfolio: {summary.get('name', 'Portfolio')}

Strategies:
{portfolio_text}

Portfolio Stats:
{stats_text}

Provide a concise analysis including:
1. Overall portfolio assessment (2-3 sentences)
2. Risk-reward balance evaluation (1-2 sentences)
3. One suggestion for portfolio improvement
4. One notable strength of the current allocation

Keep the total response under 250 words.
"""
        
        try:
            # Import here to avoid requiring OpenAI package if not used
            import openai
            
            # Create client
            client = openai.OpenAI(api_key=self.api_key)
            
            # Make API call with cost-effective model
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use the cheapest model that works well
                messages=[
                    {"role": "system", "content": "You are an expert in DeFi yield analysis. Provide concise, valuable insights for yield farmers."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=350,  # Limit token usage
                temperature=0.7
            )
            
            # Extract content
            analysis = response.choices[0].message.content.strip()
            
            # Prepare result
            result = {
                "summary": analysis,
                "portfolio_name": summary.get("name", "Portfolio"),
                "strategies_analyzed": len(strategies),
                "timestamp": datetime.now().isoformat(),
                "stats": {
                    "total_investment": total_investment,
                    "total_value": total_value,
                    "roi": roi,
                    "weighted_apy": weighted_apy
                }
            }
            
            # Cache the result
            self._save_to_cache(cache_key, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio: {e}")
            
            # Return error info
            return {
                "error": str(e),
                "summary": f"Error analyzing portfolio: {str(e)}. Please check your API key and try again.",
                "timestamp": datetime.now().isoformat()
            }

    def generate_market_trends(self, force_refresh: bool = False) -> str:
        """
        Generate market trends insights.
        
        Args:
            force_refresh: Whether to force refresh cached insights
            
        Returns:
            str: Market trends analysis
        """
        cache_key = self._get_cache_key("market_trends", datetime.now().strftime("%Y-%m-%d"))
        
        # Try to load from cache
        if not force_refresh:
            cached_insights = self._load_from_cache(cache_key)
            if cached_insights:
                return cached_insights.get("content", "No market trends available.")
        
        # If no API key, return a placeholder
        if not self.api_key:
            return "OpenAI API key not configured. Please add your API key to use AI-powered insights."
        
        try:
            import openai
            
            # Set API key
            openai.api_key = self.api_key
            
            # Create prompt
            prompt = """Provide a brief overview of current Solana yield farming market trends. Include:
1. General market sentiment
2. Key protocols performance
3. One emerging opportunity
4. One risk factor to watch

Keep it concise (3-4 paragraphs max) and focus on yield farming specifically.
"""
            
            # Make API call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in DeFi yield farming analysis, focused on Solana."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            # Get response text
            insight = response.choices[0].message.content.strip()
            
            # Cache the result
            self._save_to_cache(cache_key, {
                "content": insight,
                "timestamp": datetime.now().isoformat()
            })
            
            return insight
            
        except Exception as e:
            logger.error(f"Error generating market trends: {e}")
            return f"Error generating market trends: {str(e)}"

    def generate_risk_analysis(self, force_refresh: bool = False) -> str:
        """
        Generate risk analysis insights.
        
        Args:
            force_refresh: Whether to force refresh cached insights
            
        Returns:
            str: Risk analysis
        """
        cache_key = self._get_cache_key("risk_analysis", datetime.now().strftime("%Y-%m-%d"))
        
        # Try to load from cache
        if not force_refresh:
            cached_insights = self._load_from_cache(cache_key)
            if cached_insights:
                return cached_insights.get("content", "No risk analysis available.")
        
        # If no API key, return a placeholder
        if not self.api_key:
            return "OpenAI API key not configured. Please add your API key to use AI-powered insights."
        
        try:
            import openai
            
            # Set API key
            openai.api_key = self.api_key
            
            # Create prompt
            prompt = """Analyze the risk-reward tradeoffs in current Solana yield farming. Include:
1. How to balance APY vs security
2. Signs of unsustainable yields
3. Comparing LP vs single-asset staking risks
4. One low-risk strategy recommendation

Keep it educational and focused on helping users assess risk appropriately.
"""
            
            # Make API call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in DeFi risk assessment, specialized in Solana yield farming."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            # Get response text
            insight = response.choices[0].message.content.strip()
            
            # Cache the result
            self._save_to_cache(cache_key, {
                "content": insight,
                "timestamp": datetime.now().isoformat()
            })
            
            return insight
            
        except Exception as e:
            logger.error(f"Error generating risk analysis: {e}")
            return f"Error generating risk analysis: {str(e)}"

    def generate_portfolio_analysis(self, portfolio_data: Dict[str, Any], force_refresh: bool = False) -> str:
        """
        Generate portfolio analysis insights.
        
        Args:
            portfolio_data: Portfolio data to analyze
            force_refresh: Whether to force refresh cached insights
            
        Returns:
            str: Portfolio analysis
        """
        if not portfolio_data:
            return "No portfolio data available for analysis."
        
        # Generate data hash for cache key
        data_hash = self._generate_data_hash(portfolio_data)
        cache_key = self._get_cache_key("portfolio_analysis", data_hash)
        
        # Try to load from cache
        if not force_refresh:
            cached_insights = self._load_from_cache(cache_key)
            if cached_insights:
                return cached_insights.get("content", "No portfolio analysis available.")
        
        # If no API key, return a placeholder
        if not self.api_key:
            return "OpenAI API key not configured. Please add your API key to use AI-powered insights."
        
        try:
            import openai
            
            # Set API key
            openai.api_key = self.api_key
            
            # Extract portfolio summary
            total_value = portfolio_data.get("total_value", 0)
            roi = portfolio_data.get("roi", 0)
            weighted_apy = portfolio_data.get("weighted_apy", 0)
            strategies = portfolio_data.get("strategies", [])
            
            # Format strategy data
            strategy_text = "\n".join([
                f"- {s.get('name')}: ${s.get('initial_investment'):,.2f} invested, {s.get('apy')}% APY, Risk: {s.get('risk_level')}"
                for s in strategies[:5]  # Limit to 5 strategies to keep prompt size down
            ])
            
            # Create prompt
            prompt = f"""Analyze this yield farming portfolio:

Portfolio Value: ${total_value:,.2f}
Expected ROI: {roi:.2f}%
Weighted APY: {weighted_apy:.2f}%

Strategies:
{strategy_text}

Provide a brief analysis including:
1. Overall portfolio health and diversification
2. Risk-reward balance
3. One improvement suggestion
4. One potential concern

Keep it concise (3-4 paragraphs) and actionable.
"""
            
            # Make API call
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert in DeFi portfolio analysis, specialized in Solana yield farming."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.5
            )
            
            # Get response text
            insight = response.choices[0].message.content.strip()
            
            # Cache the result
            self._save_to_cache(cache_key, {
                "content": insight,
                "timestamp": datetime.now().isoformat()
            })
            
            return insight
            
        except Exception as e:
            logger.error(f"Error generating portfolio analysis: {e}")
            return f"Error generating portfolio analysis: {str(e)}"

# Create a global instance
yield_insights = YieldInsights()

if __name__ == "__main__":
    from src.opportunity_detector import opportunity_detector
    from src.trade_simulator import create_demo_portfolio
    
    # Test with top opportunities
    try:
        print("\n=== TESTING YIELD INSIGHTS ===")
        opportunities = opportunity_detector.get_top_opportunities(top_n=10)
        if opportunities:
            insights = yield_insights.generate_yield_summary(opportunities)
            
            if "error" in insights and "API key not found" in insights.get("error", ""):
                print("OpenAI API key not found. Skipping LLM insights test.")
            else:
                print(f"\n{insights.get('summary', 'No summary generated')}")
        else:
            print("No opportunities found for testing.")
    except Exception as e:
        print(f"Error testing yield insights: {e}")
    
    # Test with demo portfolio
    try:
        print("\n=== TESTING PORTFOLIO ANALYSIS ===")
        portfolio = create_demo_portfolio()
        portfolio_data = portfolio.to_dict()
        
        analysis = yield_insights.analyze_portfolio(portfolio_data)
        
        if "error" in analysis and "API key not found" in analysis.get("error", ""):
            print("OpenAI API key not found. Skipping portfolio analysis test.")
        else:
            print(f"\n{analysis.get('summary', 'No summary generated')}")
    except Exception as e:
        print(f"Error testing portfolio analysis: {e}") 