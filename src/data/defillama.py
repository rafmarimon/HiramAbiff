"""
DeFiLlama integration module.

This module provides functionality for fetching and processing data from
the DeFiLlama API, including TVL, yields, and protocol information.
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import httpx
import pandas as pd
from loguru import logger

from src.core.config import settings


class DeFiLlamaClient:
    """
    Client for interacting with the DeFiLlama API.
    """
    
    def __init__(self):
        """Initialize the DeFiLlama client."""
        self.base_url = settings.DEFILLAMA_API_URL
        self.api_key = settings.DEFILLAMA_API_KEY
        self.timeout = 30.0  # API request timeout in seconds
        
        # Set HTTP headers
        self.headers = {}
        if self.api_key:
            self.headers["X-API-Key"] = self.api_key
        
        logger.info(f"Initialized DeFiLlama client: {self.base_url}")
    
    async def _get_async(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make an async GET request to the DeFiLlama API.
        
        Args:
            endpoint: The API endpoint to call.
            params: Query parameters.
            
        Returns:
            Dict[str, Any]: The API response.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return {}
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {}
    
    def _get_sync(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a synchronous GET request to the DeFiLlama API.
        
        Args:
            endpoint: The API endpoint to call.
            params: Query parameters.
            
        Returns:
            Dict[str, Any]: The API response.
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params, headers=self.headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e}")
            return {}
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {}
    
    async def get_protocols(self) -> List[Dict[str, Any]]:
        """
        Get a list of all protocols tracked by DeFiLlama.
        
        Returns:
            List[Dict[str, Any]]: List of protocols.
        """
        response = await self._get_async("/protocols")
        return response.get("protocols", [])
    
    async def get_protocol(self, protocol: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific protocol.
        
        Args:
            protocol: The protocol slug (e.g., "aave-v2").
            
        Returns:
            Dict[str, Any]: Protocol details.
        """
        response = await self._get_async(f"/protocol/{protocol}")
        return response
    
    async def get_tvl(self) -> Dict[str, Any]:
        """
        Get the total value locked (TVL) across all protocols.
        
        Returns:
            Dict[str, Any]: TVL data.
        """
        response = await self._get_async("/tvl")
        return response
    
    async def get_chains(self) -> List[Dict[str, Any]]:
        """
        Get a list of all chains tracked by DeFiLlama.
        
        Returns:
            List[Dict[str, Any]]: List of chains.
        """
        response = await self._get_async("/chains")
        return response.get("chains", [])
    
    async def get_yields(self) -> List[Dict[str, Any]]:
        """
        Get yields for all protocols and pools.
        
        Returns:
            List[Dict[str, Any]]: List of yield opportunities.
        """
        response = await self._get_async("/yields")
        return response.get("data", [])
    
    async def get_yields_by_chain(self, chain: str) -> List[Dict[str, Any]]:
        """
        Get yields for a specific chain.
        
        Args:
            chain: The blockchain name (e.g., "Solana", "Ethereum").
            
        Returns:
            List[Dict[str, Any]]: List of yield opportunities for the chain.
        """
        all_yields = await self.get_yields()
        return [y for y in all_yields if y.get("chain") == chain]
    
    async def get_pools(self, protocol: str) -> List[Dict[str, Any]]:
        """
        Get pools for a specific protocol.
        
        Args:
            protocol: The protocol slug (e.g., "aave-v2").
            
        Returns:
            List[Dict[str, Any]]: List of pools.
        """
        response = await self._get_async(f"/pools/{protocol}")
        return response.get("data", [])
    
    def get_yields_dataframe(self) -> pd.DataFrame:
        """
        Get yields as a pandas DataFrame for easier analysis.
        
        Returns:
            pd.DataFrame: DataFrame of yield opportunities.
        """
        # Make a synchronous call to get yields
        response = self._get_sync("/yields")
        yields_data = response.get("data", [])
        
        if not yields_data:
            logger.warning("No yield data found")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(yields_data)
        
        # Add timestamp
        df["timestamp"] = datetime.now().isoformat()
        
        # Add APY rank
        if "apy" in df.columns:
            df["apy_rank"] = df["apy"].rank(ascending=False)
        
        # Add TVL rank
        if "tvlUsd" in df.columns:
            df["tvl_rank"] = df["tvlUsd"].rank(ascending=False)
        
        return df
    
    def find_best_yields(
        self, 
        min_apy: float = 0.0, 
        min_tvl: float = 100000.0,
        chain: Optional[str] = None,
        protocol: Optional[str] = None,
        top_n: int = 10
    ) -> pd.DataFrame:
        """
        Find the best yield opportunities based on criteria.
        
        Args:
            min_apy: Minimum APY to consider.
            min_tvl: Minimum TVL to consider.
            chain: Filter by blockchain.
            protocol: Filter by protocol.
            top_n: Number of top opportunities to return.
            
        Returns:
            pd.DataFrame: Top yield opportunities.
        """
        df = self.get_yields_dataframe()
        
        if df.empty:
            return df
        
        # Apply filters
        if min_apy > 0:
            df = df[df["apy"] >= min_apy]
        
        if min_tvl > 0:
            df = df[df["tvlUsd"] >= min_tvl]
        
        if chain:
            df = df[df["chain"] == chain]
        
        if protocol:
            df = df[df["project"] == protocol]
        
        # Sort by APY descending
        df = df.sort_values("apy", ascending=False)
        
        # Return top N results
        return df.head(top_n)


# Create a global DeFiLlama client instance
defillama_client = DeFiLlamaClient() 