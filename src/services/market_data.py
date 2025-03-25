"""
Market data service for HiramAbiff.

This module provides functionality for fetching market data for cryptocurrencies.
"""

import os
import json
import time
import datetime
from typing import Dict, List, Any, Optional
import aiohttp
import asyncio
import requests
from dotenv import load_dotenv
from loguru import logger

# Load environment variables
load_dotenv()

class MarketDataService:
    """Service for fetching market data."""
    
    def __init__(self):
        """Initialize the market data service."""
        self.coingecko_api_url = "https://api.coingecko.com/api/v3"
        self.solana_api_url = "https://api.mainnet-beta.solana.com"
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "market_cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cache the data with timestamp
        self.cached_data = {}
        self.cache_expiry = 300  # 5 minutes
    
    def get_asset_prices(self, assets: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get current prices for specified assets.
        
        Args:
            assets: List of asset symbols (e.g., ["BTC", "ETH", "SOL"])
            
        Returns:
            List of asset data dictionaries
        """
        # Check cache first
        cache_key = "asset_prices"
        if cache_key in self.cached_data:
            cache_time, cache_data = self.cached_data[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                logger.info("Using cached asset prices")
                return cache_data
        
        # Define default assets if none provided
        if assets is None:
            assets = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]
        
        # Convert ticker symbols to CoinGecko IDs if needed
        asset_ids = []
        for asset in assets:
            if asset.lower() == "btc":
                asset_ids.append("bitcoin")
            elif asset.lower() == "eth":
                asset_ids.append("ethereum")
            elif asset.lower() == "sol":
                asset_ids.append("solana")
            elif asset.lower() == "ada":
                asset_ids.append("cardano")
            elif asset.lower() == "dot":
                asset_ids.append("polkadot")
            else:
                asset_ids.append(asset.lower())
        
        # Format the asset IDs for the CoinGecko API
        ids_param = ",".join(asset_ids)
        
        try:
            # Make request to CoinGecko API
            response = requests.get(
                f"{self.coingecko_api_url}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "ids": ids_param,
                    "order": "market_cap_desc",
                    "per_page": 100,
                    "page": 1,
                    "sparkline": False,
                    "price_change_percentage": "24h",
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Transform data into our format
                result = []
                for item in data:
                    # Convert CoinGecko data to our format
                    symbol = item["symbol"].upper()
                    asset_data = {
                        "name": item["name"],
                        "symbol": symbol,
                        "price": item["current_price"],
                        "change": item["price_change_percentage_24h"] or 0,
                        "volume": item["total_volume"] / 1e9,  # Convert to billions
                        "marketCap": item["market_cap"] / 1e12,  # Convert to trillions
                    }
                    result.append(asset_data)
                
                # Cache the result
                self.cached_data[cache_key] = (time.time(), result)
                
                # Also save to disk cache
                cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
                with open(cache_file, "w") as f:
                    json.dump({
                        "timestamp": time.time(),
                        "data": result
                    }, f, indent=2)
                
                return result
            else:
                logger.error(f"Failed to fetch asset prices: {response.status_code} - {response.text}")
                return self._get_fallback_data("asset_prices")
                
        except Exception as e:
            logger.error(f"Error fetching asset prices: {e}")
            return self._get_fallback_data("asset_prices")
    
    async def get_asset_prices_async(self, assets: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get current prices for specified assets asynchronously.
        
        Args:
            assets: List of asset symbols (e.g., ["BTC", "ETH", "SOL"])
            
        Returns:
            List of asset data dictionaries
        """
        # Check cache first
        cache_key = "asset_prices"
        if cache_key in self.cached_data:
            cache_time, cache_data = self.cached_data[cache_key]
            if time.time() - cache_time < self.cache_expiry:
                logger.info("Using cached asset prices")
                return cache_data
        
        # Define default assets if none provided
        if assets is None:
            assets = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]
        
        # Convert ticker symbols to CoinGecko IDs if needed
        asset_ids = []
        for asset in assets:
            if asset.lower() == "btc":
                asset_ids.append("bitcoin")
            elif asset.lower() == "eth":
                asset_ids.append("ethereum")
            elif asset.lower() == "sol":
                asset_ids.append("solana")
            elif asset.lower() == "ada":
                asset_ids.append("cardano")
            elif asset.lower() == "dot":
                asset_ids.append("polkadot")
            else:
                asset_ids.append(asset.lower())
        
        # Format the asset IDs for the CoinGecko API
        ids_param = ",".join(asset_ids)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Make request to CoinGecko API
                async with session.get(
                    f"{self.coingecko_api_url}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "ids": ids_param,
                        "order": "market_cap_desc",
                        "per_page": 100,
                        "page": 1,
                        "sparkline": False,
                        "price_change_percentage": "24h",
                    }
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Transform data into our format
                        result = []
                        for item in data:
                            # Convert CoinGecko data to our format
                            symbol = item["symbol"].upper()
                            asset_data = {
                                "name": item["name"],
                                "symbol": symbol,
                                "price": item["current_price"],
                                "change": item["price_change_percentage_24h"] or 0,
                                "volume": item["total_volume"] / 1e9,  # Convert to billions
                                "marketCap": item["market_cap"] / 1e12,  # Convert to trillions
                            }
                            result.append(asset_data)
                        
                        # Cache the result
                        self.cached_data[cache_key] = (time.time(), result)
                        
                        # Also save to disk cache
                        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
                        with open(cache_file, "w") as f:
                            json.dump({
                                "timestamp": time.time(),
                                "data": result
                            }, f, indent=2)
                        
                        return result
                    else:
                        logger.error(f"Failed to fetch asset prices: {response.status} - {await response.text()}")
                        return self._get_fallback_data("asset_prices")
                    
        except Exception as e:
            logger.error(f"Error fetching asset prices: {e}")
            return self._get_fallback_data("asset_prices")
    
    def _get_fallback_data(self, data_type: str) -> List[Dict[str, Any]]:
        """
        Get fallback data from disk cache or static data.
        
        Args:
            data_type: Type of data to get
            
        Returns:
            List of data dictionaries
        """
        # Try to load from disk cache
        cache_file = os.path.join(self.cache_dir, f"{data_type}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r") as f:
                    cached = json.load(f)
                logger.info(f"Using disk-cached {data_type} data")
                return cached["data"]
            except Exception as e:
                logger.error(f"Error loading cached {data_type} data: {e}")
        
        # If all else fails, return static sample data
        logger.info(f"Using static sample {data_type} data")
        
        if data_type == "asset_prices":
            return [
                {"name": "Bitcoin", "symbol": "BTC", "price": 65432.10, "change": 2.3, "volume": 28.5, "marketCap": 1.25},
                {"name": "Ethereum", "symbol": "ETH", "price": 3456.78, "change": -1.2, "volume": 12.3, "marketCap": 0.42},
                {"name": "Solana", "symbol": "SOL", "price": 123.45, "change": 5.6, "volume": 6.7, "marketCap": 0.05},
                {"name": "Cardano", "symbol": "ADA", "price": 0.48, "change": 0.8, "volume": 5.2, "marketCap": 0.02},
                {"name": "Polkadot", "symbol": "DOT", "price": 6.72, "change": -2.1, "volume": 3.1, "marketCap": 0.01},
            ]
        else:
            return []

# Create a global market data service instance
market_data_service = MarketDataService() 