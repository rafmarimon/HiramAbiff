#!/usr/bin/env python
"""
LLM Agent for HiramAbiff

This module provides an interface to OpenAI's API for generating insights
about yield farming opportunities, portfolio management, and market analysis.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache directory setup
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

class LLMAgent:
    """
    Agent for interacting with OpenAI API and generating insights.
    """
    
    def __init__(self, api_key: str = None, cache_ttl: int = 3600):
        """
        Initialize the LLM agent.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY environment variable)
            cache_ttl: Time-to-live for cached data in seconds (default: 1 hour)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.cache_ttl = cache_ttl
        
        # Track calls to manage rate limiting
        self.call_count = 0
        self.last_call_time = 0
        
        if not self.api_key:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the path to a cache file for a given key."""
        # Create a safe filename from the key
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return CACHE_DIR / f"llm_cache_{safe_key}.json"
    
    def _load_from_cache(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load data from cache if it exists and is not expired.
        
        Args:
            key: Cache key
            
        Returns:
            Dict or None: Cached data or None if not found or expired
        """
        cache_path = self._get_cache_path(key)
        
        if not cache_path.exists():
            return None
        
        try:
            # Check if cache is expired
            mtime = cache_path.stat().st_mtime
            if time.time() - mtime > self.cache_ttl:
                logger.debug(f"Cache expired for {key}")
                return None
            
            # Load cache
            with open(cache_path, "r") as f:
                data = json.load(f)
                logger.info(f"Loaded LLM response from cache for {key}")
                return data
        except Exception as e:
            logger.error(f"Error loading from cache: {e}")
            return None
    
    def _save_to_cache(self, key: str, data: Dict[str, Any]) -> None:
        """
        Save data to cache.
        
        Args:
            key: Cache key
            data: Data to cache
        """
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, "w") as f:
                json.dump(data, f)
                logger.debug(f"Saved LLM response to cache for {key}")
        except Exception as e:
            logger.error(f"Error saving to cache: {e}")
    
    def _call_openai_api(self, prompt: str, model: str = "gpt-3.5-turbo", max_tokens: int = 150) -> str:
        """
        Call OpenAI API with rate limiting and error handling.
        
        Args:
            prompt: Prompt to send to OpenAI
            model: OpenAI model to use
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            str: Generated text
        """
        if not self.api_key:
            return "API key not set. Please set OPENAI_API_KEY environment variable."
        
        # Rate limiting (3 second minimum between calls)
        now = time.time()
        time_since_last_call = now - self.last_call_time
        if time_since_last_call < 3:
            time.sleep(3 - time_since_last_call)
        
        try:
            # Import OpenAI module here to handle potential ImportError better
            import openai
            
            # Set API key
            openai.api_key = self.api_key
            
            # Create messages for the chat API
            messages = [
                {"role": "system", "content": "You are a helpful DeFi analyst providing concise insights."},
                {"role": "user", "content": prompt}
            ]
            
            # Make request using the new API format
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
            
            # Update call tracking
            self.call_count += 1
            self.last_call_time = time.time()
            
            # Extract the content from the message
            return response.choices[0].message.content.strip()
            
        except ImportError:
            return "OpenAI module not installed. Please install with 'pip install openai>=1.0.0'."
        
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return f"Error calling API: {str(e)}"
    
    def generate_yield_insights(self, opportunities: List[Dict[str, Any]], force_refresh: bool = False) -> str:
        """
        Generate insights for yield opportunities.
        
        Args:
            opportunities: List of yield opportunities
            force_refresh: Whether to force a refresh of cached data
            
        Returns:
            str: Generated insights
        """
        if not opportunities:
            return "No opportunities provided for analysis."
        
        # Create a cache key based on the opportunities
        cache_key = f"yield_insights_{hash(json.dumps(opportunities, sort_keys=True))}"
        
        # Try to load from cache if not forcing a refresh
        if not force_refresh:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data.get("insight", "")
        
        # Format yield data for prompt
        yield_data = "\n".join([
            f"- {opp.get('project', 'Unknown')}: {opp.get('symbol', 'Unknown')} - {opp.get('apy', 0):.2f}% APY, " +
            f"Risk: {opp.get('risk_level', 'Unknown')}, TVL: ${opp.get('tvlUsd', 0):,.0f}"
            for opp in opportunities[:5]
        ])
        
        # Create prompt
        prompt = f"""
        Analyze the following Solana DeFi yield opportunities:
        
        {yield_data}
        
        Provide a 2-3 sentence summary of the best opportunities and any notable insights.
        Focus on APY, risk level, and any interesting patterns. Keep your response under 100 words.
        """
        
        # Call API
        insight = self._call_openai_api(prompt)
        
        # Save to cache
        self._save_to_cache(cache_key, {"insight": insight})
        
        return insight
    
    def generate_portfolio_advice(self, portfolio_data: Dict[str, Any], force_refresh: bool = False) -> str:
        """
        Generate advice for a portfolio.
        
        Args:
            portfolio_data: Portfolio data
            force_refresh: Whether to force a refresh of cached data
            
        Returns:
            str: Generated advice
        """
        if not portfolio_data:
            return "No portfolio data provided for analysis."
        
        # Create a cache key based on the portfolio data
        cache_key = f"portfolio_advice_{hash(json.dumps(portfolio_data, sort_keys=True))}"
        
        # Try to load from cache if not forcing a refresh
        if not force_refresh:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data.get("advice", "")
        
        # Format portfolio data for prompt
        strategies = portfolio_data.get("strategies", [])
        portfolio_value = portfolio_data.get("total_value", 0)
        profit = portfolio_data.get("profit", 0)
        
        strategies_text = "\n".join([
            f"- {strategy.get('name', 'Unknown')} - " +
            f"Invested: ${strategy.get('initial_investment', 0):,.2f}, " +
            f"Current: ${strategy.get('current_value', 0):,.2f}, " +
            f"APY: {strategy.get('apy', 0):.2f}%"
            for strategy in strategies[:5]
        ])
        
        # Create prompt
        prompt = f"""
        Analyze the following yield farming portfolio:
        
        Total Value: ${portfolio_value:,.2f}
        Profit: ${profit:,.2f}
        
        Strategies:
        {strategies_text}
        
        Provide 2-3 sentences of advice on how to optimize this portfolio.
        Consider risk diversification, APY optimization, and potential rebalancing.
        Keep your response under 100 words.
        """
        
        # Call API
        advice = self._call_openai_api(prompt)
        
        # Save to cache
        self._save_to_cache(cache_key, {"advice": advice})
        
        return advice
    
    def generate_market_summary(self, market_data: Dict[str, Any], force_refresh: bool = False) -> str:
        """
        Generate a summary of market conditions.
        
        Args:
            market_data: Market data
            force_refresh: Whether to force a refresh of cached data
            
        Returns:
            str: Generated summary
        """
        if not market_data:
            return "No market data provided for analysis."
        
        # Create a cache key based on the market data
        cache_key = f"market_summary_{hash(json.dumps(market_data, sort_keys=True))}"
        
        # Try to load from cache if not forcing a refresh
        if not force_refresh:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data.get("summary", "")
        
        # Format market data for prompt
        tokens = market_data.get("tokens", [])
        
        tokens_text = "\n".join([
            f"- {token.get('symbol', 'Unknown')}: ${token.get('price', 0):,.6f}, " +
            f"24h: {token.get('price_change_24h', 0):+.2f}%, " +
            f"7d: {token.get('price_change_7d', 0):+.2f}%"
            for token in tokens[:5]
        ])
        
        # Create prompt
        prompt = f"""
        Analyze the following Solana token prices:
        
        {tokens_text}
        
        Provide a brief 2-3 sentence market summary focused on these tokens.
        Note any significant price movements or trends.
        Keep your response under 100 words.
        """
        
        # Call API
        summary = self._call_openai_api(prompt)
        
        # Save to cache
        self._save_to_cache(cache_key, {"summary": summary})
        
        return summary

# Create singleton instance
llm_agent = LLMAgent() 