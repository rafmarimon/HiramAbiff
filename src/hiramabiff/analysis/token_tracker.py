#!/usr/bin/env python
"""
Token Tracker Module

This module provides functionality for tracking and analyzing cryptocurrency tokens
across different blockchains. It includes features for fetching token prices,
historical data, and performing analysis.
"""

import os
import json
import time
import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dotenv import load_dotenv
from loguru import logger

# Try to load environment variables
load_dotenv()


class TokenTracker:
    """A class for tracking and analyzing token data."""
    
    # Map of common token symbols to their IDs on CoinGecko
    TOKEN_MAP = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "USDC": "usd-coin",
        "USDT": "tether",
        "DOT": "polkadot",
        "ADA": "cardano",
        "AVAX": "avalanche-2",
        "BNB": "binancecoin",
        "MATIC": "matic-network",
    }
    
    def __init__(self, data_dir: str = None):
        """Initialize the token tracker.
        
        Args:
            data_dir: Directory for storing token data
        """
        # Set up data directory
        if data_dir is None:
            home_dir = os.path.expanduser("~")
            self.data_dir = os.path.join(home_dir, ".hiramabiff", "data", "tokens")
        else:
            self.data_dir = data_dir
            
        # Create data directories if they don't exist
        os.makedirs(os.path.join(self.data_dir, "prices"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "analysis"), exist_ok=True)
        
        # Load API keys from environment variables
        self.etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
        self.alchemy_api_key = os.getenv("ALCHEMY_API_KEY")
        self.infura_api_key = os.getenv("INFURA_API_KEY")
        
        # Endpoints
        self.coingecko_api = "https://api.coingecko.com/api/v3"
        self.etherscan_api = "https://api.etherscan.io/api"
        
        # Set up Ethereum RPC endpoint
        self.ethereum_rpc = os.getenv("ETHEREUM_RPC_URL", "https://mainnet.infura.io/v3/")
        
        if self.infura_api_key and not self.ethereum_rpc.endswith(self.infura_api_key):
            self.ethereum_rpc = f"{self.ethereum_rpc}{self.infura_api_key}"
        elif self.alchemy_api_key and not "alchemy" in self.ethereum_rpc:
            self.ethereum_rpc = f"https://eth-mainnet.g.alchemy.com/v2/{self.alchemy_api_key}"
            
        # Set up Solana RPC endpoint
        self.solana_rpc = os.getenv("ALCHEMY_SOLANA_URL", 
                                   os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com"))
        
        logger.info(f"Initialized TokenTracker with Solana RPC: {self.solana_rpc}")
        logger.info(f"Initialized TokenTracker with Ethereum RPC: {self.ethereum_rpc.split('/v2/')[0]}/v2/...")
        
        # Cache to store token prices
        self.price_cache = {}
        self.price_cache_expiry = {}
        self.cache_duration = 300  # 5 minutes
        
    async def get_token_price(self, symbol: str) -> Dict[str, Any]:
        """Get the current price of a token.
        
        Args:
            symbol: Token symbol (e.g., BTC, ETH)
            
        Returns:
            Dict containing token price and other market data
        """
        # Check if we have a fresh cached price
        now = time.time()
        symbol = symbol.upper()
        
        if symbol in self.price_cache and now < self.price_cache_expiry.get(symbol, 0):
            logger.debug(f"Using cached price for {symbol}")
            return self.price_cache[symbol]
        
        # Convert symbol to coingecko id if in our map
        token_id = self.TOKEN_MAP.get(symbol, symbol.lower())
        
        # If the symbol is not in our map, we'll try to use it directly
        # This might fail if it's not a valid CoinGecko ID
        
        logger.info(f"Fetching price for {symbol} (ID: {token_id})")
        
        async with aiohttp.ClientSession() as session:
            try:
                # Use CoinGecko's simple price endpoint
                url = f"{self.coingecko_api}/simple/price"
                params = {
                    "ids": token_id,
                    "vs_currencies": "usd",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true",
                    "include_24hr_change": "true",
                    "include_last_updated_at": "true"
                }
                
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    if token_id not in data:
                        raise ValueError(f"Token {symbol} not found (ID: {token_id})")
                    
                    token_data = data[token_id]
                    
                    # Format the response
                    price_data = {
                        "symbol": symbol,
                        "id": token_id,
                        "price_usd": token_data["usd"],
                        "market_cap_usd": token_data["usd_market_cap"],
                        "volume_24h_usd": token_data["usd_24h_vol"],
                        "change_24h_percent": token_data["usd_24h_change"],
                        "last_updated": datetime.fromtimestamp(token_data["last_updated_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    
                    # Cache the result
                    self.price_cache[symbol] = price_data
                    self.price_cache_expiry[symbol] = now + self.cache_duration
                    
                    return price_data
                    
            except aiohttp.ClientError as e:
                logger.error(f"Error fetching price for {symbol}: {str(e)}")
                raise ValueError(f"Failed to fetch price for {symbol}: {str(e)}")
            except KeyError as e:
                logger.error(f"Error parsing price data for {symbol}: {str(e)}")
                raise ValueError(f"Failed to parse price data for {symbol}: {str(e)}")
    
    async def get_token_historical_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """Get historical price data for a token.
        
        Args:
            symbol: Token symbol (e.g., BTC, ETH)
            days: Number of days of historical data to fetch
            
        Returns:
            DataFrame containing historical price data
        """
        symbol = symbol.upper()
        token_id = self.TOKEN_MAP.get(symbol, symbol.lower())
        
        # Check if we have the data saved
        csv_path = os.path.join(self.data_dir, "prices", f"{symbol}_history_{days}d.csv")
        
        # If we have recent data, load it
        if os.path.exists(csv_path):
            file_mod_time = os.path.getmtime(csv_path)
            if time.time() - file_mod_time < 3600:  # less than 1 hour old
                logger.debug(f"Loading cached historical data for {symbol}")
                return pd.read_csv(csv_path, parse_dates=["timestamp"])
        
        logger.info(f"Fetching {days} days of historical data for {symbol}")
        
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.coingecko_api}/coins/{token_id}/market_chart"
                params = {
                    "vs_currency": "usd",
                    "days": days,
                    "interval": "daily" if days > 90 else "hourly"
                }
                
                async with session.get(url, params=params) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Process the data
                    prices = data["prices"]
                    market_caps = data["market_caps"]
                    volumes = data["total_volumes"]
                    
                    # Create a DataFrame
                    df = pd.DataFrame(prices, columns=["timestamp", "price"])
                    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
                    
                    # Add market caps and volumes
                    df["market_cap"] = [row[1] for row in market_caps]
                    df["volume"] = [row[1] for row in volumes]
                    
                    # Save to CSV
                    df.to_csv(csv_path, index=False)
                    
                    return df
                    
            except aiohttp.ClientError as e:
                logger.error(f"Error fetching historical data for {symbol}: {str(e)}")
                raise ValueError(f"Failed to fetch historical data for {symbol}: {str(e)}")
    
    async def analyze_token(self, symbol: str) -> Dict[str, Any]:
        """Analyze a token and return statistical metrics.
        
        Args:
            symbol: Token symbol (e.g., BTC, ETH)
            
        Returns:
            Dict containing analysis results
        """
        symbol = symbol.upper()
        
        # Get current price data
        current_price_data = await self.get_token_price(symbol)
        
        # Get historical data - 30 days
        historical_data = await self.get_token_historical_data(symbol, days=30)
        
        # Calculate statistical metrics
        mean_price = historical_data["price"].mean()
        min_price = historical_data["price"].min()
        max_price = historical_data["price"].max()
        std_dev = historical_data["price"].std()
        volatility = std_dev / mean_price
        
        # Calculate 7-day change
        if len(historical_data) >= 7:
            week_ago_price = historical_data.iloc[-7]["price"]
            current_price = historical_data.iloc[-1]["price"]
            change_7d = ((current_price - week_ago_price) / week_ago_price) * 100
        else:
            change_7d = 0
        
        # Create analysis result
        analysis = {
            "symbol": symbol,
            "id": current_price_data["id"],
            "current_price_usd": current_price_data["price_usd"],
            "market_cap_usd": current_price_data["market_cap_usd"],
            "volume_24h_usd": current_price_data["volume_24h_usd"],
            "change_24h_percent": current_price_data["change_24h_percent"],
            "change_7d_percent": change_7d,
            "stats": {
                "mean_price_30d": mean_price,
                "min_price_30d": min_price,
                "max_price_30d": max_price,
                "std_dev_30d": std_dev,
                "volatility_30d": volatility,
            },
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Save analysis to file
        analysis_path = os.path.join(self.data_dir, "analysis", f"{symbol}_analysis.json")
        with open(analysis_path, "w") as f:
            json.dump(analysis, f, indent=2)
        
        return analysis
    
    async def get_wallet_token_balances(self, chain: str, address: str) -> Dict[str, Any]:
        """Get token balances for a wallet.
        
        Args:
            chain: Blockchain name (e.g., ethereum, solana)
            address: Wallet address
            
        Returns:
            Dict containing token balances
        """
        chain = chain.lower()
        result = {
            "chain": chain,
            "address": address,
            "native_balance": 0,
            "tokens": [],
            "retrieved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        if chain == "ethereum":
            # Ethereum - use Etherscan API to get token balances
            if not self.etherscan_api_key:
                raise ValueError("Etherscan API key not found. Set ETHERSCAN_API_KEY in .env")
            
            async with aiohttp.ClientSession() as session:
                # Get ETH balance
                try:
                    params = {
                        "module": "account",
                        "action": "balance",
                        "address": address,
                        "tag": "latest",
                        "apikey": self.etherscan_api_key
                    }
                    
                    async with session.get(self.etherscan_api, params=params) as response:
                        response.raise_for_status()
                        data = await response.json()
                        
                        if data["status"] == "1":
                            eth_balance = int(data["result"]) / 1e18
                            result["native_balance"] = eth_balance
                        else:
                            logger.warning(f"Etherscan API error: {data['message']}")
                
                    # Get ERC-20 token balances
                    params = {
                        "module": "account",
                        "action": "tokentx",
                        "address": address,
                        "page": 1,
                        "offset": 100,
                        "sort": "desc",
                        "apikey": self.etherscan_api_key
                    }
                    
                    async with session.get(self.etherscan_api, params=params) as response:
                        response.raise_for_status()
                        data = await response.json()
                        
                        if data["status"] == "1":
                            # Process token transactions to find current balances
                            token_balances = {}
                            
                            for tx in data["result"]:
                                token_addr = tx["contractAddress"]
                                token_name = tx["tokenName"]
                                token_symbol = tx["tokenSymbol"]
                                token_decimals = int(tx["tokenDecimal"])
                                
                                # Skip if we've already processed this token
                                if token_addr in token_balances:
                                    continue
                                
                                # Get token balance
                                token_params = {
                                    "module": "account",
                                    "action": "tokenbalance",
                                    "contractaddress": token_addr,
                                    "address": address,
                                    "tag": "latest",
                                    "apikey": self.etherscan_api_key
                                }
                                
                                async with session.get(self.etherscan_api, params=token_params) as token_response:
                                    token_data = await token_response.json()
                                    
                                    if token_data["status"] == "1" and int(token_data["result"]) > 0:
                                        token_balance = int(token_data["result"]) / (10 ** token_decimals)
                                        
                                        # Get USD value if possible
                                        usd_value = None
                                        try:
                                            price_data = await self.get_token_price(token_symbol)
                                            usd_value = token_balance * price_data["price_usd"]
                                        except Exception as e:
                                            logger.debug(f"Could not get USD value for {token_symbol}: {str(e)}")
                                        
                                        token_balances[token_addr] = {
                                            "name": token_name,
                                            "symbol": token_symbol,
                                            "balance": token_balance,
                                            "usd_value": usd_value
                                        }
                            
                            # Add tokens to result
                            result["tokens"] = list(token_balances.values())
                        else:
                            logger.warning(f"Etherscan API error: {data['message']}")
                
                except aiohttp.ClientError as e:
                    logger.error(f"Error fetching Ethereum wallet data: {str(e)}")
                    raise ValueError(f"Failed to fetch Ethereum wallet data: {str(e)}")
                    
        elif chain == "solana":
            # Solana - use RPC API to get token balances
            if not self.solana_rpc:
                raise ValueError("Solana RPC URL not found. Set SOLANA_RPC_URL in .env")
            
            async with aiohttp.ClientSession() as session:
                try:
                    # Get SOL balance
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [address]
                    }
                    
                    async with session.post(self.solana_rpc, json=payload) as response:
                        response.raise_for_status()
                        data = await response.json()
                        
                        if "result" in data:
                            sol_balance = data["result"]["value"] / 1e9
                            result["native_balance"] = sol_balance
                        else:
                            logger.warning(f"Solana RPC error: {data['error']['message']}")
                    
                    # Get SPL tokens
                    payload = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTokenAccountsByOwner",
                        "params": [
                            address,
                            {
                                "programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
                            },
                            {
                                "encoding": "jsonParsed"
                            }
                        ]
                    }
                    
                    async with session.post(self.solana_rpc, json=payload) as response:
                        response.raise_for_status()
                        data = await response.json()
                        
                        if "result" in data:
                            token_accounts = data["result"]["value"]
                            
                            for account in token_accounts:
                                token_info = account["account"]["data"]["parsed"]["info"]
                                mint = token_info["mint"]
                                token_amount = token_info["tokenAmount"]
                                
                                if token_amount["uiAmount"] > 0:
                                    # Get token metadata
                                    # Note: In a real implementation, you'd want to use a token metadata service
                                    # or on-chain data to get the token name and symbol
                                    token_name = mint[:6]  # Placeholder
                                    token_symbol = mint[:4]  # Placeholder
                                    
                                    result["tokens"].append({
                                        "mint": mint,
                                        "name": token_name,
                                        "symbol": token_symbol,
                                        "balance": token_amount["uiAmount"],
                                        "usd_value": None
                                    })
                        else:
                            logger.warning(f"Solana RPC error: {data['error']['message']}")
                            
                except aiohttp.ClientError as e:
                    logger.error(f"Error fetching Solana wallet data: {str(e)}")
                    raise ValueError(f"Failed to fetch Solana wallet data: {str(e)}")
        
        else:
            raise ValueError(f"Unsupported chain: {chain}")
        
        return result
    
    async def generate_portfolio_analysis(self, wallets: Dict[str, str]) -> Dict[str, Any]:
        """Generate analysis for a portfolio of wallet addresses.
        
        Args:
            wallets: Dict of chain to wallet address mappings
            
        Returns:
            Dict containing portfolio analysis
        """
        portfolio = {
            "wallets": wallets,
            "tokens": [],
            "total_value_usd": 0,
            "token_distribution": {},
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Process each wallet
        for chain, address in wallets.items():
            try:
                wallet_data = await self.get_wallet_token_balances(chain, address)
                
                # Add native token
                native_symbol = "ETH" if chain.lower() == "ethereum" else "SOL"
                native_price = await self.get_token_price(native_symbol)
                
                native_usd_value = wallet_data["native_balance"] * native_price["price_usd"]
                portfolio["total_value_usd"] += native_usd_value
                
                # Add to token distribution
                if native_symbol in portfolio["token_distribution"]:
                    portfolio["token_distribution"][native_symbol]["value_usd"] += native_usd_value
                else:
                    portfolio["token_distribution"][native_symbol] = {
                        "value_usd": native_usd_value,
                        "percentage": 0  # will calculate percentages at the end
                    }
                
                # Process other tokens
                for token in wallet_data["tokens"]:
                    if token["usd_value"]:
                        portfolio["total_value_usd"] += token["usd_value"]
                        
                        # Add to token distribution
                        if token["symbol"] in portfolio["token_distribution"]:
                            portfolio["token_distribution"][token["symbol"]]["value_usd"] += token["usd_value"]
                        else:
                            portfolio["token_distribution"][token["symbol"]] = {
                                "value_usd": token["usd_value"],
                                "percentage": 0  # will calculate percentages at the end
                            }
                
                # Add wallet data to portfolio
                portfolio["tokens"].extend(wallet_data["tokens"])
                
            except Exception as e:
                logger.error(f"Error processing wallet {chain}:{address}: {str(e)}")
        
        # Calculate percentages
        if portfolio["total_value_usd"] > 0:
            for token, data in portfolio["token_distribution"].items():
                data["percentage"] = (data["value_usd"] / portfolio["total_value_usd"]) * 100
        
        # Save portfolio analysis
        portfolio_filename = f"portfolio_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        portfolio_path = os.path.join(self.data_dir, "analysis", portfolio_filename)
        
        with open(portfolio_path, "w") as f:
            json.dump(portfolio, f, indent=2)
        
        return portfolio 