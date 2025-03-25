#!/usr/bin/env python
"""
Wallet Manager Module

This module provides functionality for managing cryptocurrency wallets
across different blockchains, with a focus on Solana.
"""

import os
import json
import base58
import secrets
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import asyncio

# For Solana
try:
    from solders.keypair import Keypair
    from solana.rpc.async_api import AsyncClient as SolanaAsyncClient
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False

# For Ethereum (stub for now)
try:
    from eth_account import Account
    from web3 import Web3, AsyncHTTPProvider
    from web3.eth import AsyncEth
    ETHEREUM_AVAILABLE = True
except ImportError:
    ETHEREUM_AVAILABLE = False

class WalletManager:
    """
    Manages cryptocurrency wallets across different blockchains.
    
    This class provides functionality for creating, importing, and managing
    wallets for various blockchains, with a focus on Solana.
    """
    
    def __init__(self, wallet_dir: Optional[str] = None):
        """
        Initialize the wallet manager.
        
        Args:
            wallet_dir: Directory to store wallet files. If None, uses ~/.hiramabiff/wallets
        """
        if wallet_dir is None:
            # Default to ~/.hiramabiff/wallets
            self.wallet_dir = os.path.expanduser(os.path.join("~", ".hiramabiff", "wallets"))
        else:
            self.wallet_dir = wallet_dir
            
        # Create directory if it doesn't exist
        os.makedirs(self.wallet_dir, exist_ok=True)
        
        # Initialize clients
        self.solana_client = None
        self.ethereum_client = None
        
        # Cache of loaded wallets
        self._wallets = {}
        
    async def init_clients(self):
        """Initialize blockchain clients asynchronously."""
        # Initialize Solana client if available
        if SOLANA_AVAILABLE:
            # Prioritize Alchemy Solana URL if available
            solana_rpc_url = os.environ.get("ALCHEMY_SOLANA_URL")
            if not solana_rpc_url:
                solana_rpc_url = os.environ.get("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
            
            print(f"Connecting to Solana via: {solana_rpc_url.split('/v2/')[0]}/v2/...")
            self.solana_client = SolanaAsyncClient(solana_rpc_url)
            
        # Initialize Ethereum client if available
        if ETHEREUM_AVAILABLE:
            # Prioritize direct Ethereum RPC URL setting
            eth_rpc_url = os.environ.get("ETHEREUM_RPC_URL")
            
            # If not set but Alchemy API key is available, use that
            if not eth_rpc_url:
                alchemy_key = os.environ.get("ALCHEMY_API_KEY")
                if alchemy_key:
                    eth_rpc_url = f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}"
                else:
                    eth_rpc_url = "https://mainnet.infura.io/v3/YOUR_PROJECT_ID"
            
            print(f"Connecting to Ethereum via: {eth_rpc_url.split('/v2/')[0] if '/v2/' in eth_rpc_url else eth_rpc_url}/...")
            self.ethereum_client = Web3(AsyncHTTPProvider(eth_rpc_url), modules={"eth": (AsyncEth,)})
    
    def create_wallet(self, chain: str, name: str) -> Dict[str, Any]:
        """
        Create a new wallet for the specified blockchain.
        
        Args:
            chain: Blockchain to create wallet for (e.g., "solana", "ethereum")
            name: Name for the wallet
            
        Returns:
            Dict containing wallet information
        
        Raises:
            ValueError: If the chain is not supported or other validation errors
        """
        chain = chain.lower()
        
        # Validate name (alphanumeric and hyphens only)
        if not name.replace("-", "").isalnum():
            raise ValueError("Wallet name must contain only alphanumeric characters and hyphens")
        
        # Check if wallet with this name already exists
        wallet_path = os.path.join(self.wallet_dir, f"{name}.json")
        if os.path.exists(wallet_path):
            raise ValueError(f"Wallet with name '{name}' already exists")
        
        wallet_info = {
            "name": name,
            "chain": chain,
            "created_at": "2025-03-22T00:00:00Z",  # Placeholder timestamp for now
        }
        
        if chain == "solana":
            if not SOLANA_AVAILABLE:
                raise ValueError("Solana support is not available. Install the solana package.")
            
            # Generate a new Solana keypair
            keypair = Keypair()
            
            # Add Solana-specific wallet info
            wallet_info.update({
                "public_key": str(keypair.pubkey()),
                "private_key_b58": base58.b58encode(bytes(keypair.secret())).decode("utf-8"),
            })
            
        elif chain == "ethereum":
            if not ETHEREUM_AVAILABLE:
                raise ValueError("Ethereum support is not available. Install the web3 package.")
            
            # Generate a new Ethereum account
            account = Account.create()
            
            # Add Ethereum-specific wallet info
            wallet_info.update({
                "address": account.address,
                "private_key": account.key.hex(),
            })
            
        else:
            raise ValueError(f"Unsupported blockchain: {chain}")
        
        # Save wallet to file
        with open(wallet_path, "w") as f:
            json.dump(wallet_info, f, indent=2)
            
        # Add to cache
        self._wallets[name] = wallet_info
            
        return wallet_info
    
    def import_wallet(self, chain: str, name: str, private_key: str) -> Dict[str, Any]:
        """
        Import an existing wallet using its private key.
        
        Args:
            chain: Blockchain the wallet belongs to
            name: Name for the wallet
            private_key: Private key for the wallet
            
        Returns:
            Dict containing wallet information
        
        Raises:
            ValueError: If the chain is not supported or other validation errors
        """
        chain = chain.lower()
        
        # Validate name (alphanumeric and hyphens only)
        if not name.replace("-", "").isalnum():
            raise ValueError("Wallet name must contain only alphanumeric characters and hyphens")
        
        # Check if wallet with this name already exists
        wallet_path = os.path.join(self.wallet_dir, f"{name}.json")
        if os.path.exists(wallet_path):
            raise ValueError(f"Wallet with name '{name}' already exists")
        
        wallet_info = {
            "name": name,
            "chain": chain,
            "created_at": "2025-03-22T00:00:00Z",  # Placeholder timestamp for now
            "imported": True,
        }
        
        if chain == "solana":
            if not SOLANA_AVAILABLE:
                raise ValueError("Solana support is not available. Install the solana package.")
            
            try:
                # Try to interpret as a base58 private key
                decoded = base58.b58decode(private_key)
                
                # Create keypair from secret
                if len(decoded) == 64:  # Full keypair (both public and private)
                    keypair = Keypair.from_bytes(decoded)
                elif len(decoded) == 32:  # Just the secret key
                    keypair = Keypair.from_seed(decoded)
                else:
                    raise ValueError("Invalid Solana private key length")
                
                # Add Solana-specific wallet info
                wallet_info.update({
                    "public_key": str(keypair.pubkey()),
                    "private_key_b58": base58.b58encode(bytes(keypair.secret())).decode("utf-8"),
                })
                
            except Exception as e:
                raise ValueError(f"Invalid Solana private key: {str(e)}")
            
        elif chain == "ethereum":
            if not ETHEREUM_AVAILABLE:
                raise ValueError("Ethereum support is not available. Install the web3 package.")
            
            try:
                # Try to create an account from the private key
                account = Account.from_key(private_key)
                
                # Add Ethereum-specific wallet info
                wallet_info.update({
                    "address": account.address,
                    "private_key": account.key.hex(),
                })
                
            except Exception as e:
                raise ValueError(f"Invalid Ethereum private key: {str(e)}")
            
        else:
            raise ValueError(f"Unsupported blockchain: {chain}")
        
        # Save wallet to file
        with open(wallet_path, "w") as f:
            json.dump(wallet_info, f, indent=2)
            
        # Add to cache
        self._wallets[name] = wallet_info
            
        return wallet_info
    
    def list_wallets(self) -> List[Dict[str, Any]]:
        """
        List all wallets managed by this instance.
        
        Returns:
            List of wallet information dictionaries
        """
        wallets = []
        
        # Ensure wallet directory exists
        if not os.path.exists(self.wallet_dir):
            return wallets
        
        # Load all wallet files
        for filename in os.listdir(self.wallet_dir):
            if filename.endswith(".json"):
                try:
                    wallet_path = os.path.join(self.wallet_dir, filename)
                    with open(wallet_path, "r") as f:
                        wallet_info = json.load(f)
                        
                        # Skip non-wallet files
                        if "name" not in wallet_info or "chain" not in wallet_info:
                            continue
                        
                        # Mask private key
                        if "private_key" in wallet_info:
                            wallet_info["private_key"] = "***MASKED***"
                        if "private_key_b58" in wallet_info:
                            wallet_info["private_key_b58"] = "***MASKED***"
                        
                        wallets.append(wallet_info)
                        
                        # Update cache
                        self._wallets[wallet_info["name"]] = wallet_info
                except Exception as e:
                    print(f"Error loading wallet {filename}: {str(e)}")
                    
        return wallets
    
    def get_wallet(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information for a specific wallet.
        
        Args:
            name: Name of the wallet
            
        Returns:
            Wallet information or None if not found
        """
        # Check cache first
        if name in self._wallets:
            return self._wallets[name]
            
        # Try to load from file
        wallet_path = os.path.join(self.wallet_dir, f"{name}.json")
        if not os.path.exists(wallet_path):
            return None
            
        try:
            with open(wallet_path, "r") as f:
                wallet_info = json.load(f)
                
                # Mask private key for return value
                wallet_info_masked = wallet_info.copy()
                if "private_key" in wallet_info_masked:
                    wallet_info_masked["private_key"] = "***MASKED***"
                if "private_key_b58" in wallet_info_masked:
                    wallet_info_masked["private_key_b58"] = "***MASKED***"
                
                # Update cache with unmasked version
                self._wallets[name] = wallet_info
                
                return wallet_info_masked
        except Exception as e:
            print(f"Error loading wallet {name}: {str(e)}")
            return None
            
    def get_wallet_with_private_key(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get information for a specific wallet, including private key.
        
        Args:
            name: Name of the wallet
            
        Returns:
            Wallet information or None if not found
        """
        # Try to load from file (don't use cache to ensure we have the latest)
        wallet_path = os.path.join(self.wallet_dir, f"{name}.json")
        if not os.path.exists(wallet_path):
            return None
            
        try:
            with open(wallet_path, "r") as f:
                wallet_info = json.load(f)
                # Update cache
                self._wallets[name] = wallet_info
                return wallet_info
        except Exception as e:
            print(f"Error loading wallet {name}: {str(e)}")
            return None
    
    def delete_wallet(self, name: str) -> bool:
        """
        Delete a wallet.
        
        Args:
            name: Name of the wallet
            
        Returns:
            True if deleted, False if not found
        """
        wallet_path = os.path.join(self.wallet_dir, f"{name}.json")
        if not os.path.exists(wallet_path):
            return False
            
        try:
            os.remove(wallet_path)
            
            # Remove from cache
            if name in self._wallets:
                del self._wallets[name]
                
            return True
        except Exception as e:
            print(f"Error deleting wallet {name}: {str(e)}")
            return False
    
    async def get_balance(self, name: str) -> Dict[str, Any]:
        """
        Get balance for a wallet across supported blockchains.
        
        Args:
            name: Name of the wallet
            
        Returns:
            Dict with balance information
            
        Raises:
            ValueError: If wallet not found or other error
        """
        wallet = self.get_wallet(name)
        if wallet is None:
            raise ValueError(f"Wallet '{name}' not found")
            
        chain = wallet["chain"].lower()
        
        if chain == "solana":
            if not SOLANA_AVAILABLE:
                raise ValueError("Solana support is not available")
                
            if self.solana_client is None:
                await self.init_clients()
                
            try:
                public_key = wallet["public_key"]
                response = await self.solana_client.get_balance(public_key)
                
                # Balance is in lamports (1 SOL = 10^9 lamports)
                balance_lamports = response.value
                balance_sol = balance_lamports / 1_000_000_000
                
                return {
                    "chain": "solana",
                    "wallet": name,
                    "address": public_key,
                    "balance": {
                        "lamports": balance_lamports,
                        "sol": balance_sol,
                    }
                }
            except Exception as e:
                raise ValueError(f"Error getting Solana balance: {str(e)}")
                
        elif chain == "ethereum":
            if not ETHEREUM_AVAILABLE:
                raise ValueError("Ethereum support is not available")
                
            if self.ethereum_client is None:
                await self.init_clients()
                
            try:
                address = wallet["address"]
                balance_wei = await self.ethereum_client.eth.get_balance(address)
                
                # Balance is in wei (1 ETH = 10^18 wei)
                balance_eth = balance_wei / 1_000_000_000_000_000_000
                
                return {
                    "chain": "ethereum",
                    "wallet": name,
                    "address": address,
                    "balance": {
                        "wei": balance_wei,
                        "eth": balance_eth,
                    }
                }
            except Exception as e:
                raise ValueError(f"Error getting Ethereum balance: {str(e)}")
                
        else:
            raise ValueError(f"Unsupported blockchain: {chain}") 