#!/usr/bin/env python
"""
Solana Testnet Example

This script demonstrates basic interactions with the Solana testnet using the HiramAbiff system.
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from solana.publickey import PublicKey
from solana.rpc.types import TokenAccountOpts
from solana.transaction import Transaction, TransactionInstruction

from src.blockchain.solana_client import SolanaClientManager, NetworkType
from src.blockchain.wallet import wallet_manager
from src.core.logger import setup_logging


async def get_network_info(client_manager):
    """
    Get basic information about the Solana network.
    
    Args:
        client_manager: The Solana client manager
    """
    logger.info("Fetching network information...")
    
    # Get the version of the Solana node
    version = await client_manager.async_client.get_version()
    if "result" in version:
        logger.info(f"Solana version: {version['result']['solana-core']}")
    
    # Get the latest blockhash
    blockhash = await client_manager.async_client.get_recent_blockhash()
    if "result" in blockhash:
        logger.info(f"Recent blockhash: {blockhash['result']['value']['blockhash']}")
    
    # Get the current slot
    slot = await client_manager.async_client.get_slot()
    if "result" in slot:
        logger.info(f"Current slot: {slot['result']}")
    
    # Get the current leader
    leader = await client_manager.async_client.get_slot_leader()
    if "result" in leader:
        logger.info(f"Current slot leader: {leader['result']}")
    
    logger.info("Network information fetched")


async def explore_wallet(client_manager, wallet_name):
    """
    Explore a wallet's details on the Solana testnet.
    
    Args:
        client_manager: The Solana client manager
        wallet_name: Name of the wallet to explore
    """
    # Get the wallet keypair
    keypair = wallet_manager.get_wallet(wallet_name)
    if not keypair:
        logger.error(f"Wallet '{wallet_name}' not found")
        return
    
    pubkey = keypair.public_key
    logger.info(f"Exploring wallet: {wallet_name} ({pubkey})")
    
    # Get SOL balance
    balance = await client_manager.get_balance_async(pubkey)
    logger.info(f"SOL Balance: {balance} SOL")
    
    # Get token accounts
    token_accounts = await client_manager.get_token_accounts_async(pubkey)
    logger.info(f"Found {len(token_accounts)} token accounts")
    
    for account in token_accounts:
        pubkey_str = account["pubkey"]
        account_data = account["account"]["data"]
        
        # For token accounts, data is encoded in "mint" and "owner" fields
        logger.info(f"Token Account: {pubkey_str}")
        
        # You would typically decode the token account data here
        # But for simplicity, we'll just log the raw data
        logger.info(f"  Program: {account['account']['owner']}")
        
    # Get transaction history
    # Note: This is simplified and would need more work for a complete history
    logger.info("Recent transactions for this wallet:")
    signatures = await client_manager.async_client.get_signatures_for_address(pubkey, limit=5)
    
    if "result" in signatures:
        for sig_info in signatures["result"]:
            sig = sig_info["signature"]
            slot = sig_info["slot"]
            err = sig_info.get("err")
            status = "Failed" if err else "Success"
            
            logger.info(f"  Tx: {sig[:10]}...{sig[-10:]} | Slot: {slot} | Status: {status}")
    else:
        logger.info("  No transactions found")


async def example_transfer(client_manager, from_wallet, to_wallet, amount_sol):
    """
    Example of transferring SOL between wallets.
    
    Args:
        client_manager: The Solana client manager
        from_wallet: Name of the source wallet
        to_wallet: Name of the destination wallet
        amount_sol: Amount of SOL to transfer
    
    Returns:
        bool: True if the transfer was successful, False otherwise
    """
    # This is just a simulation for educational purposes
    # In a real application, you would properly construct and send the transaction
    
    # Get the wallet keypairs
    from_keypair = wallet_manager.get_wallet(from_wallet)
    if not from_keypair:
        logger.error(f"Source wallet '{from_wallet}' not found")
        return False
    
    to_pubkey = None
    to_wallet_obj = wallet_manager.get_wallet(to_wallet)
    if to_wallet_obj:
        to_pubkey = to_wallet_obj.public_key
    else:
        # Assume to_wallet is a public key string
        try:
            to_pubkey = PublicKey(to_wallet)
        except Exception as e:
            logger.error(f"Invalid destination wallet: {e}")
            return False
    
    # Convert SOL to lamports
    amount_lamports = int(amount_sol * 10**9)
    
    logger.info(f"Preparing to transfer {amount_sol} SOL from {from_wallet} to {to_pubkey}")
    
    # Check if the source has enough SOL
    from_balance = await client_manager.get_balance_async(from_keypair.public_key)
    if from_balance < amount_sol:
        logger.error(f"Insufficient balance: {from_balance} SOL")
        return False
    
    # Get recent blockhash
    blockhash_resp = await client_manager.async_client.get_recent_blockhash()
    if "result" not in blockhash_resp:
        logger.error("Failed to get recent blockhash")
        return False
    
    recent_blockhash = blockhash_resp["result"]["value"]["blockhash"]
    
    # Create a transfer instruction
    # Note: In a real application, you would use the System Program to create this
    logger.info("Creating transfer transaction (simulated)")
    logger.info(f"  From: {from_keypair.public_key}")
    logger.info(f"  To: {to_pubkey}")
    logger.info(f"  Amount: {amount_sol} SOL ({amount_lamports} lamports)")
    logger.info(f"  Recent blockhash: {recent_blockhash}")
    
    # We're not actually sending this transaction, just simulating it
    return True


async def main():
    """Main function for the example."""
    logger.info("Starting Solana Testnet Example")
    
    # Initialize Solana client for testnet
    client_manager = SolanaClientManager(network_type=NetworkType.TESTNET)
    logger.info(f"Initialized Solana client for {NetworkType.TESTNET}")
    
    try:
        # Get basic network information
        await get_network_info(client_manager)
        
        # Create a new test wallet if needed
        test_wallet = wallet_manager.get_wallet("test")
        if not test_wallet:
            logger.info("Creating new test wallet")
            test_pubkey, _ = wallet_manager.create_wallet("test")
            logger.info(f"Created test wallet with public key: {test_pubkey}")
        else:
            test_pubkey = str(test_wallet.public_key)
            logger.info(f"Loaded existing test wallet: {test_pubkey}")
        
        # Explore the wallet details
        await explore_wallet(client_manager, "test")
        
        # Simulate a transfer (not actually sending)
        # Replace these with your actual wallet names or addresses
        await example_transfer(client_manager, "test", "GKNcUmNacSJo4S2Kq3DuYRYRGw3sNUfJ4tyqd198t6vQ", 0.01)
        
        logger.info("Example completed. Note that no actual transactions were sent.")
        logger.info("This was just a simulation for educational purposes.")
    
    finally:
        # Close the client connections
        client_manager.close()


if __name__ == "__main__":
    # Set up logging
    setup_logging()
    
    # Run the example
    asyncio.run(main()) 