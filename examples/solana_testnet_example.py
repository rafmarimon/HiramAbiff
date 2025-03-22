#!/usr/bin/env python
"""
Solana Testnet Example

This script demonstrates how to interact with the Solana testnet using the HiramAbiff framework.
It shows basic operations like creating a wallet, checking balance, and simulating a transaction.
"""

import os
import asyncio
import secrets
import base58
from pathlib import Path
from loguru import logger
import httpx

# Solana imports
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.transaction import Transaction
from solders.message import Message
from solders.instruction import Instruction, AccountMeta
from solders.system_program import transfer, TransferParams
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Confirmed
from solana.exceptions import SolanaRpcException

# Set up logging
logger.add("solana_example.log", rotation="10 MB")

async def main():
    """Run the Solana testnet example."""
    logger.info("Starting Solana testnet example")
    
    # Connect to Solana testnet
    url = "https://api.testnet.solana.com"
    client = AsyncClient(url, commitment=Confirmed)
    logger.info(f"Connected to Solana testnet at {url}")
    
    try:
        # Generate a new wallet keypair
        seed = secrets.token_bytes(32)
        keypair = Keypair.from_seed(bytes(seed))
        public_key = keypair.pubkey()
        
        # Convert private key to base58 for display (this is the format used in wallet files)
        private_key_bytes = keypair.secret()
        private_key_b58 = base58.b58encode(private_key_bytes).decode('ascii')
        
        logger.info(f"Generated new wallet with public key: {public_key}")
        logger.info(f"Private key (base58): {private_key_b58}")
        
        # Check account balance
        balance_response = await client.get_balance(public_key)
        balance = balance_response.value
        logger.info(f"Account balance: {balance} lamports")
        
        # Get network information
        version = await client.get_version()
        logger.info(f"Solana version: {version}")
        
        recent_blockhash_response = await client.get_latest_blockhash()
        blockhash = recent_blockhash_response.value.blockhash
        logger.info(f"Recent blockhash: {blockhash}")
        
        # Simulate a transfer (won't actually send since we have 0 balance)
        recipient_pubkey = Pubkey.find_program_address([b"recipient"], Pubkey(bytes([0]*32)))[0]
        logger.info(f"Simulating transfer to: {recipient_pubkey}")
        
        # Create transfer instruction
        transfer_ix = transfer(
            TransferParams(
                from_pubkey=public_key,
                to_pubkey=recipient_pubkey,
                lamports=1000
            )
        )
        
        # Create a message containing our instruction
        message = Message([transfer_ix], public_key)
        
        # Create a transaction with the message
        transaction = Transaction([keypair], message, blockhash)
        
        # Note: In a real application with sufficient balance, we would send the transaction:
        # signature = await client.send_transaction(transaction)
        logger.info("Transfer transaction created (not sent due to 0 balance)")
        
        # Get some testnet accounts to demonstrate querying - with rate limiting error handling
        try:
            largest_accounts = await client.get_largest_accounts()
            if largest_accounts and largest_accounts.value:
                logger.info(f"Largest account: {largest_accounts.value[0].address} with {largest_accounts.value[0].lamports} lamports")
        except (SolanaRpcException, httpx.HTTPStatusError) as e:
            if "429" in str(e):
                logger.warning("Rate limit exceeded when trying to fetch largest accounts. This is normal with public RPC endpoints.")
            else:
                logger.error(f"Error fetching largest accounts: {str(e)}")
        
        logger.info("Example completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in Solana example: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        # Close the client connection
        await client.close()
        logger.info("Solana example completed")

if __name__ == "__main__":
    asyncio.run(main()) 