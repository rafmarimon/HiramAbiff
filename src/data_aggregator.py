#!/usr/bin/env python
"""
Data Aggregator for HiramAbiff

This module fetches yield data from DeFi Llama and other sources, with a focus on
Solana DeFi protocols like Raydium and Orca. It includes caching mechanisms to 
minimize API calls.
"""

import os
import time
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import requests
import pandas as pd

# Cache directory setup
CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

class DataAggregator:
    """
    Aggregates yield and DeFi data from various sources with caching support
    to minimize API calls.
    """
    
    def __init__(self, cache_ttl: int = 3600):
        """
        Initialize the data aggregator with caching support.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 1 hour)
        """
        self.cache_ttl = cache_ttl
        self.defillama_base_url = "https://yields.llama.fi/pools"
        
        # URL for specific Solana protocols
        self.solana_specific_urls = {
            "raydium": "https://yields.llama.fi/poolsEnriched?project=raydium",
            "orca": "https://yields.llama.fi/poolsEnriched?project=orca-protocol",
            "marinade": "https://yields.llama.fi/poolsEnriched?project=marinade-finance",
            "solend": "https://yields.llama.fi/poolsEnriched?project=solend",
            "jupiter": "https://yields.llama.fi/poolsEnriched?project=jupiter",
        }
    
    def _get_cache_path(self, key: str) -> Path:
        """Get the path to a cache file for a given key."""
        # Create a safe filename from the key
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return CACHE_DIR / f"{safe_key}.json"
    
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
                print(f"Cache expired for {key}")
                return None
            
            # Load cache
            with open(cache_path, "r") as f:
                data = json.load(f)
                print(f"Loaded {key} data from cache")
                return data
        except Exception as e:
            print(f"Error loading from cache: {e}")
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
                print(f"Saved {key} data to cache")
        except Exception as e:
            print(f"Error saving to cache: {e}")
    
    def fetch_solana_yields(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch yield data for Solana DeFi protocols.
        
        Args:
            force_refresh: Whether to force refreshing cached data
            
        Returns:
            List[Dict[str, Any]]: List of yield opportunities on Solana
        """
        cache_key = "solana_yields"
        
        # Try to load from cache if not forcing a refresh
        if not force_refresh:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data.get("data", [])
        
        try:
            print("Fetching Solana yield data from DeFi Llama...")
            
            # Fetch data for Solana chain
            response = requests.get(
                f"{self.defillama_base_url}?chain=solana", 
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                pools = result.get("data", [])
                
                # Add timestamp for cache freshness tracking
                data_with_meta = {
                    "data": pools,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "source": "defillama"
                }
                
                # Save to cache
                self._save_to_cache(cache_key, data_with_meta)
                
                return pools
            else:
                print(f"Error fetching Solana yield data: HTTP {response.status_code}")
                # Fall back to cache even if it's expired
                cached_data = self._load_from_cache(cache_key)
                if cached_data:
                    print("Using expired cache data as fallback")
                    return cached_data.get("data", [])
                return []
                
        except Exception as e:
            print(f"Error fetching Solana yield data: {e}")
            # Fall back to cache even if it's expired
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                print("Using expired cache data as fallback")
                return cached_data.get("data", [])
            return []
    
    def fetch_protocol_yields(self, protocol: str, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Fetch yield data for a specific protocol.
        
        Args:
            protocol: Protocol name (e.g., "raydium", "orca")
            force_refresh: Whether to force refreshing cached data
            
        Returns:
            List[Dict[str, Any]]: List of yield opportunities for the protocol
        """
        cache_key = f"{protocol}_yields"
        
        # Try to load from cache if not forcing a refresh
        if not force_refresh:
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                return cached_data.get("data", [])
        
        # Check if we have a specific URL for this protocol
        if protocol not in self.solana_specific_urls:
            print(f"No specific URL for protocol: {protocol}")
            return []
        
        protocol_url = self.solana_specific_urls[protocol]
        
        try:
            print(f"Fetching yield data for {protocol} from DeFi Llama...")
            
            response = requests.get(protocol_url, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                pools = result.get("data", [])
                
                # Add timestamp for cache freshness tracking
                data_with_meta = {
                    "data": pools,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "source": "defillama"
                }
                
                # Save to cache
                self._save_to_cache(cache_key, data_with_meta)
                
                return pools
            else:
                print(f"Error fetching {protocol} yield data: HTTP {response.status_code}")
                # Fall back to cache even if it's expired
                cached_data = self._load_from_cache(cache_key)
                if cached_data:
                    print("Using expired cache data as fallback")
                    return cached_data.get("data", [])
                return []
                
        except Exception as e:
            print(f"Error fetching {protocol} yield data: {e}")
            # Fall back to cache even if it's expired
            cached_data = self._load_from_cache(cache_key)
            if cached_data:
                print("Using expired cache data as fallback")
                return cached_data.get("data", [])
            return []
    
    def get_all_solana_protocols_yields(self, force_refresh: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get yield data for all supported Solana protocols.
        
        Args:
            force_refresh: Whether to force refreshing cached data
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary of protocol name to list of yield opportunities
        """
        results = {}
        
        for protocol in self.solana_specific_urls.keys():
            yields = self.fetch_protocol_yields(protocol, force_refresh)
            if yields:
                results[protocol] = yields
        
        return results
    
    def get_yields_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Convert yield data to a pandas DataFrame for easier analysis.
        
        Args:
            data: List of yield opportunities
            
        Returns:
            pd.DataFrame: DataFrame of yield opportunities
        """
        if not data:
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Add timestamp
        df["timestamp"] = datetime.datetime.now().isoformat()
        
        # Calculate and add ranks if needed columns exist
        if "apy" in df.columns:
            df["apy_rank"] = df["apy"].rank(ascending=False)
        
        if "tvlUsd" in df.columns:
            df["tvl_rank"] = df["tvlUsd"].rank(ascending=False)
        
        return df

# Create a global instance
data_aggregator = DataAggregator()

if __name__ == "__main__":
    # Simple test
    aggregator = DataAggregator()
    solana_yields = aggregator.fetch_solana_yields()
    print(f"Found {len(solana_yields)} Solana yield opportunities")
    
    # Get Raydium yields specifically
    raydium_yields = aggregator.fetch_protocol_yields("raydium")
    print(f"Found {len(raydium_yields)} Raydium yield opportunities") 