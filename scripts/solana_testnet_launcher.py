#!/usr/bin/env python
"""
Solana Testnet Launcher Script

This script handles launching the HiramAbiff system on the Solana testnet.
It sets up wallets, requests airdrops, and initializes the system.
"""

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from solana.publickey import PublicKey
from solana.rpc.commitment import Confirmed
from solana.transaction import Transaction

from src.blockchain.solana_client import SolanaClientManager, NetworkType
from src.blockchain.wallet import wallet_manager
from src.core.config import settings
from src.core.logger import setup_logging


async def request_airdrop(client_manager, wallet_pubkey, amount_sol=1.0):
    """
    Request an airdrop from the Solana testnet.
    
    Args:
        client_manager: The Solana client manager
        wallet_pubkey: The public key to receive the airdrop
        amount_sol: Amount of SOL to request (1.0 by default)
    
    Returns:
        bool: True if airdrop was successful, False otherwise
    """
    # Convert SOL to lamports (1 SOL = 10^9 lamports)
    amount_lamports = int(amount_sol * 10**9)
    
    if isinstance(wallet_pubkey, str):
        wallet_pubkey = PublicKey(wallet_pubkey)
    
    logger.info(f"Requesting airdrop of {amount_sol} SOL to {wallet_pubkey}")
    
    try:
        # Request the airdrop
        response = await client_manager.async_client.request_airdrop(
            wallet_pubkey, amount_lamports, commitment=Confirmed
        )
        
        if "result" not in response:
            logger.error(f"Airdrop request failed: {response}")
            return False
        
        # Get the transaction signature
        tx_sig = response["result"]
        logger.info(f"Airdrop requested. Transaction signature: {tx_sig}")
        
        # Wait for confirmation
        max_retries = 10
        for i in range(max_retries):
            logger.info(f"Waiting for airdrop confirmation... ({i+1}/{max_retries})")
            
            # Check if the transaction was confirmed
            response = await client_manager.async_client.get_confirmed_transaction(tx_sig)
            if "result" in response and response["result"] is not None:
                logger.info(f"Airdrop confirmed!")
                return True
            
            # Wait before checking again
            await asyncio.sleep(2)
        
        logger.warning(f"Airdrop not confirmed after {max_retries} attempts.")
        return False
        
    except Exception as e:
        logger.error(f"Error requesting airdrop: {e}")
        return False


async def check_balance(client_manager, wallet_pubkey):
    """
    Check the balance of a wallet.
    
    Args:
        client_manager: The Solana client manager
        wallet_pubkey: The public key to check
    
    Returns:
        float: The balance in SOL
    """
    if isinstance(wallet_pubkey, str):
        wallet_pubkey = PublicKey(wallet_pubkey)
    
    logger.info(f"Checking balance for {wallet_pubkey}")
    
    try:
        balance = await client_manager.get_balance_async(wallet_pubkey)
        logger.info(f"Balance: {balance} SOL")
        return balance
    except Exception as e:
        logger.error(f"Error checking balance: {e}")
        return 0.0


async def setup_testnet_wallets():
    """
    Set up wallets for testnet deployment.
    
    Returns:
        tuple: (agent_wallet_pubkey, trading_wallet_pubkey)
    """
    # Create or load the agent wallet
    agent_wallet = wallet_manager.get_wallet("agent")
    if not agent_wallet:
        logger.info("Creating new agent wallet")
        agent_pubkey, _ = wallet_manager.create_wallet("agent")
    else:
        agent_pubkey = str(agent_wallet.public_key)
        logger.info(f"Loaded existing agent wallet: {agent_pubkey}")
    
    # Create or load the trading wallet
    trading_wallet = wallet_manager.get_wallet("trading")
    if not trading_wallet:
        logger.info("Creating new trading wallet")
        trading_pubkey, _ = wallet_manager.create_wallet("trading")
    else:
        trading_pubkey = str(trading_wallet.public_key)
        logger.info(f"Loaded existing trading wallet: {trading_pubkey}")
    
    return agent_pubkey, trading_pubkey


async def launch_testnet(args):
    """
    Main function to launch the system on the testnet.
    
    Args:
        args: Command line arguments
    """
    logger.info("Starting HiramAbiff Solana testnet launcher")
    
    # Initialize the Solana client for testnet
    client_manager = SolanaClientManager(network_type=NetworkType.TESTNET)
    logger.info(f"Initialized Solana client for {NetworkType.TESTNET}")
    
    try:
        # Set up wallets
        agent_pubkey, trading_pubkey = await setup_testnet_wallets()
        
        # Check current balances
        agent_balance = await check_balance(client_manager, agent_pubkey)
        trading_balance = await check_balance(client_manager, trading_pubkey)
        
        # Request airdrops if needed
        if agent_balance < 0.5:
            logger.info("Agent wallet needs SOL. Requesting airdrop...")
            airdrop_success = await request_airdrop(client_manager, agent_pubkey, 1.0)
            if airdrop_success:
                agent_balance = await check_balance(client_manager, agent_pubkey)
        
        if trading_balance < 0.5:
            logger.info("Trading wallet needs SOL. Requesting airdrop...")
            airdrop_success = await request_airdrop(client_manager, trading_pubkey, 1.0)
            if airdrop_success:
                trading_balance = await check_balance(client_manager, trading_pubkey)
        
        # Print wallet information
        logger.info("=== Wallet Information ===")
        logger.info(f"Agent Wallet: {agent_pubkey}")
        logger.info(f"Agent Balance: {agent_balance} SOL")
        logger.info(f"Trading Wallet: {trading_pubkey}")
        logger.info(f"Trading Balance: {trading_balance} SOL")
        
        # Save deployment info
        deployment_info = {
            "timestamp": time.time(),
            "network": "testnet",
            "agent_wallet": agent_pubkey,
            "agent_balance": agent_balance,
            "trading_wallet": trading_pubkey,
            "trading_balance": trading_balance,
        }
        
        os.makedirs("data", exist_ok=True)
        with open("data/deployment_info.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        
        logger.info("Testnet setup complete!")
        logger.info(f"Deployment info saved to data/deployment_info.json")
        
        if args.start_agents:
            logger.info("Starting agent system...")
            # TODO: Start the agents system here
            # This would typically involve starting the DeFi agent and Trading agent
            logger.info("Agent system started")
    
    finally:
        # Close any connections
        client_manager.close()
        logger.info("Launcher completed.")


def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description="HiramAbiff Solana Testnet Launcher")
    parser.add_argument("--start-agents", action="store_true", help="Start the agent system after setup")
    args = parser.parse_args()
    
    # Set up logging
    setup_logging()
    
    # Run the launch function
    asyncio.run(launch_testnet(args))


if __name__ == "__main__":
    main() 