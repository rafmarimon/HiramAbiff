"""
Solana wallet management module.

This module provides functionality for managing Solana wallets, 
including loading existing wallets, creating new wallets, and
signing transactions.
"""

import base58
import json
import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

from loguru import logger
from solana.keypair import Keypair
from solana.publickey import PublicKey
from solana.rpc.commitment import Confirmed
from solana.transaction import Transaction

from src.core.config import settings


class WalletManager:
    """
    Manager for Solana wallet operations.
    
    This class handles operations related to Solana wallets:
    - Loading and saving keypairs
    - Managing multiple wallets
    - Signing transactions
    """
    
    def __init__(self, wallet_dir: Optional[Path] = None):
        """
        Initialize the wallet manager.
        
        Args:
            wallet_dir: Directory to store wallet files. Defaults to ~/.hiramabiff/wallets/
        """
        if wallet_dir is None:
            # Default to ~/.hiramabiff/wallets/
            self.wallet_dir = Path.home() / ".hiramabiff" / "wallets"
        else:
            self.wallet_dir = wallet_dir
            
        # Create the wallet directory if it doesn't exist
        self.wallet_dir.mkdir(parents=True, exist_ok=True)
        
        # Currently loaded keypairs
        self._keypairs: Dict[str, Keypair] = {}
        
        logger.info(f"Initialized wallet manager with wallet directory: {self.wallet_dir}")
    
    def create_wallet(self, name: str) -> Tuple[str, str]:
        """
        Create a new wallet.
        
        Args:
            name: Name of the wallet.
            
        Returns:
            Tuple[str, str]: Public key and private key in base58 format.
        """
        keypair = Keypair()
        public_key = str(keypair.public_key)
        private_key = base58.b58encode(bytes(keypair.secret_key)).decode("ascii")
        
        # Store in memory
        self._keypairs[name] = keypair
        
        # Save to file
        wallet_path = self.wallet_dir / f"{name}.json"
        
        wallet_data = {
            "name": name,
            "public_key": public_key,
            "private_key": private_key
        }
        
        with open(wallet_path, "w") as f:
            json.dump(wallet_data, f, indent=2)
        
        logger.info(f"Created new wallet '{name}' with public key: {public_key}")
        return public_key, private_key
    
    def load_wallet(self, name: str) -> Optional[Tuple[str, str]]:
        """
        Load a wallet from disk.
        
        Args:
            name: Name of the wallet.
            
        Returns:
            Optional[Tuple[str, str]]: Public key and private key in base58 format if found.
        """
        wallet_path = self.wallet_dir / f"{name}.json"
        
        if not wallet_path.exists():
            logger.error(f"Wallet '{name}' not found at {wallet_path}")
            return None
        
        try:
            with open(wallet_path, "r") as f:
                wallet_data = json.load(f)
            
            public_key = wallet_data["public_key"]
            private_key = wallet_data["private_key"]
            
            # Recreate the keypair from the private key
            secret_key = base58.b58decode(private_key)
            keypair = Keypair.from_secret_key(secret_key)
            
            # Store in memory
            self._keypairs[name] = keypair
            
            logger.info(f"Loaded wallet '{name}' with public key: {public_key}")
            return public_key, private_key
        
        except Exception as e:
            logger.error(f"Failed to load wallet '{name}': {e}")
            return None
    
    def get_wallet(self, name: str) -> Optional[Keypair]:
        """
        Get a wallet keypair by name.
        
        Args:
            name: Name of the wallet.
            
        Returns:
            Optional[Keypair]: The keypair if found.
        """
        if name in self._keypairs:
            return self._keypairs[name]
        
        # Try to load from disk
        result = self.load_wallet(name)
        if result:
            return self._keypairs[name]
        
        return None
    
    def sign_transaction(self, name: str, transaction: Transaction) -> Optional[Transaction]:
        """
        Sign a transaction with a wallet.
        
        Args:
            name: Name of the wallet.
            transaction: Transaction to sign.
            
        Returns:
            Optional[Transaction]: The signed transaction if successful.
        """
        keypair = self.get_wallet(name)
        if not keypair:
            logger.error(f"Wallet '{name}' not found")
            return None
        
        try:
            transaction.sign([keypair])
            return transaction
        
        except Exception as e:
            logger.error(f"Failed to sign transaction: {e}")
            return None
    
    def list_wallets(self) -> Dict[str, str]:
        """
        List all available wallets.
        
        Returns:
            Dict[str, str]: Dictionary mapping wallet names to public keys.
        """
        wallets = {}
        
        for wallet_file in self.wallet_dir.glob("*.json"):
            try:
                with open(wallet_file, "r") as f:
                    wallet_data = json.load(f)
                
                name = wallet_data["name"]
                public_key = wallet_data["public_key"]
                wallets[name] = public_key
            
            except Exception as e:
                logger.warning(f"Failed to read wallet file {wallet_file}: {e}")
        
        return wallets


# Create a global wallet manager instance
wallet_manager = WalletManager() 