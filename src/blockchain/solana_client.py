"""
Solana blockchain client module.

This module provides functionality for interacting with the Solana blockchain,
including account management, transaction handling, and program interaction.
"""

import asyncio
import json
import os
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import solana
from loguru import logger
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.api import Client as SolanaClient
from solana.rpc.async_api import AsyncClient as AsyncSolanaClient
from solana.rpc.commitment import Confirmed, Finalized, Processed
from solana.rpc.types import TxOpts
from solana.transaction import Transaction

from src.core.config import settings


class NetworkType(str, Enum):
    """Solana network types."""
    MAINNET = "mainnet"
    TESTNET = "testnet"
    DEVNET = "devnet"


class SolanaClientManager:
    """
    Manages Solana client connections and provides utility methods for 
    common Solana operations.
    """
    
    def __init__(self, network_type: NetworkType = NetworkType.MAINNET):
        """
        Initialize a Solana client manager.
        
        Args:
            network_type: The Solana network to connect to.
        """
        self.network_type = network_type
        self._client = None
        self._async_client = None
        
        # Set the appropriate RPC URL based on network type
        if network_type == NetworkType.MAINNET:
            self.rpc_url = settings.SOLANA_RPC_URL
        elif network_type == NetworkType.TESTNET:
            self.rpc_url = settings.SOLANA_RPC_URL_TESTNET
        elif network_type == NetworkType.DEVNET:
            self.rpc_url = settings.SOLANA_RPC_URL_DEVNET
        else:
            raise ValueError(f"Invalid network type: {network_type}")
        
        logger.info(f"Initialized Solana client for {network_type} network")
    
    @property
    def client(self) -> SolanaClient:
        """
        Get or create a Solana client.
        
        Returns:
            SolanaClient: The Solana client.
        """
        if self._client is None:
            self._client = SolanaClient(self.rpc_url)
        return self._client
    
    @property
    def async_client(self) -> AsyncSolanaClient:
        """
        Get or create an async Solana client.
        
        Returns:
            AsyncSolanaClient: The async Solana client.
        """
        if self._async_client is None:
            self._async_client = AsyncSolanaClient(self.rpc_url)
        return self._async_client
    
    def get_balance(self, public_key: Union[str, PublicKey]) -> float:
        """
        Get the SOL balance of an account.
        
        Args:
            public_key: The public key of the account.
            
        Returns:
            float: The SOL balance.
        """
        if isinstance(public_key, str):
            public_key = PublicKey(public_key)
        
        response = self.client.get_balance(public_key)
        if "result" in response and "value" in response["result"]:
            # Convert lamports to SOL (1 SOL = 10^9 lamports)
            return response["result"]["value"] / 10**9
        else:
            logger.error(f"Failed to get balance: {response}")
            return 0.0
    
    async def get_balance_async(self, public_key: Union[str, PublicKey]) -> float:
        """
        Get the SOL balance of an account asynchronously.
        
        Args:
            public_key: The public key of the account.
            
        Returns:
            float: The SOL balance.
        """
        if isinstance(public_key, str):
            public_key = PublicKey(public_key)
        
        response = await self.async_client.get_balance(public_key)
        if "result" in response and "value" in response["result"]:
            # Convert lamports to SOL (1 SOL = 10^9 lamports)
            return response["result"]["value"] / 10**9
        else:
            logger.error(f"Failed to get balance: {response}")
            return 0.0
    
    def get_account_info(self, public_key: Union[str, PublicKey]) -> Dict[str, Any]:
        """
        Get information about an account.
        
        Args:
            public_key: The public key of the account.
            
        Returns:
            Dict[str, Any]: The account information.
        """
        if isinstance(public_key, str):
            public_key = PublicKey(public_key)
        
        response = self.client.get_account_info(public_key)
        if "result" in response and "value" in response["result"]:
            return response["result"]["value"]
        else:
            logger.error(f"Failed to get account info: {response}")
            return {}
    
    async def get_account_info_async(self, public_key: Union[str, PublicKey]) -> Dict[str, Any]:
        """
        Get information about an account asynchronously.
        
        Args:
            public_key: The public key of the account.
            
        Returns:
            Dict[str, Any]: The account information.
        """
        if isinstance(public_key, str):
            public_key = PublicKey(public_key)
        
        response = await self.async_client.get_account_info(public_key)
        if "result" in response and "value" in response["result"]:
            return response["result"]["value"]
        else:
            logger.error(f"Failed to get account info: {response}")
            return {}
    
    def create_keypair(self) -> Keypair:
        """
        Create a new Solana keypair.
        
        Returns:
            Keypair: The generated keypair.
        """
        return Keypair()
    
    def get_token_accounts(self, owner: Union[str, PublicKey]) -> List[Dict[str, Any]]:
        """
        Get all token accounts owned by an address.
        
        Args:
            owner: The owner's public key.
            
        Returns:
            List[Dict[str, Any]]: List of token accounts.
        """
        if isinstance(owner, str):
            owner = PublicKey(owner)
        
        response = self.client.get_token_accounts_by_owner(
            owner,
            {"programId": PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")},
        )
        
        if "result" in response and "value" in response["result"]:
            return response["result"]["value"]
        else:
            logger.error(f"Failed to get token accounts: {response}")
            return []
    
    async def get_token_accounts_async(self, owner: Union[str, PublicKey]) -> List[Dict[str, Any]]:
        """
        Get all token accounts owned by an address asynchronously.
        
        Args:
            owner: The owner's public key.
            
        Returns:
            List[Dict[str, Any]]: List of token accounts.
        """
        if isinstance(owner, str):
            owner = PublicKey(owner)
        
        response = await self.async_client.get_token_accounts_by_owner(
            owner,
            {"programId": PublicKey("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")},
        )
        
        if "result" in response and "value" in response["result"]:
            return response["result"]["value"]
        else:
            logger.error(f"Failed to get token accounts: {response}")
            return []
    
    def close(self) -> None:
        """Close the client connections."""
        if self._async_client:
            asyncio.create_task(self._async_client.close())
            self._async_client = None
        
        if self._client:
            # The synchronous client doesn't have a close method,
            # but we set it to None to allow garbage collection
            self._client = None
        
        logger.info("Closed Solana client connections")


# Create a default Solana client manager instance
solana_client_manager = SolanaClientManager(network_type=NetworkType.MAINNET) 