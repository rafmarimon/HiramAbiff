# HiramAbiff Examples

This directory contains example scripts that demonstrate how to use the HiramAbiff framework for building DeFi agents and interacting with blockchain networks, with a focus on Solana.

## Quick Start

To run any example, make sure you have installed the HiramAbiff package and its dependencies:

```bash
# From the project root directory
pip install -e .
```

Then run an example:

```bash
python examples/simple_solana_test.py
```

## Available Examples

### Basic Solana Connectivity

1. **simple_solana_test.py**
   - A minimal test script to verify Solana connectivity
   - Tests basic operations like connecting to the Solana testnet, retrieving version info, and generating keypairs
   - Recommended as a first step to ensure your Solana setup works correctly

2. **solana_testnet_example.py**
   - Demonstrates how to launch a Solana testnet application
   - Shows how to create wallets, check balances, and make simple transactions

### DeFi Agents

3. **minimal_defi_agent.py**
   - A dependency-free implementation of a DeFi agent
   - Simulates fetching and analyzing yield farming opportunities
   - Demonstrates the core concepts of yield analysis without external API calls
   - Great for understanding the basic architecture of agents

4. **defi_agent_example.py**
   - Basic demonstration of the DeFi agent functionality
   - Shows how to initialize a DeFi agent, search for yield opportunities across blockchains
   - Focuses on retrieving and filtering opportunities based on APY and TVL

5. **advanced_defi_agent_example.py**
   - Advanced example showing how to extend the base DeFi agent
   - Creates a specialized Solana arbitrage agent that finds both yield farming and arbitrage opportunities
   - Demonstrates how to build custom strategies by combining different DeFi opportunities
   - Includes a nicely formatted report of findings

### Multi-Agent Systems

6. **agent_collaboration_example.py**
   - Shows how multiple agents can work together in a coordinated fashion
   - Demonstrates agent communication and task delegation
   - Includes examples of how to create a simple multi-agent system for more complex DeFi strategies

## Example Usage Patterns

### For Beginners

If you're new to the HiramAbiff framework or Solana development:

1. Start with `simple_solana_test.py` to ensure your environment is set up correctly
2. Try `minimal_defi_agent.py` to understand the concept of DeFi agents without external dependencies
3. Explore `solana_testnet_example.py` to learn about Solana-specific operations

### For Advanced Users

If you're looking to build custom DeFi agents or complex strategies:

1. Study `advanced_defi_agent_example.py` to learn how to extend the base agent classes
2. Explore `agent_collaboration_example.py` to understand multi-agent coordination
3. Use these examples as templates for building your own specialized agents

## Environment Variables

Many examples require environment variables to be set. You can create a `.env` file in the project root with:

```
# Solana RPC URLs
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_RPC_URL_TESTNET=https://api.testnet.solana.com
SOLANA_RPC_URL_DEVNET=https://api.devnet.solana.com

# DeFiLlama API
DEFILLAMA_API_URL=https://yields.llama.fi/
DEFILLAMA_API_KEY=  # Optional

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE=hiram.log
```

## Contributing

Feel free to add your own examples! If you create a useful example that demonstrates a feature of the HiramAbiff framework:

1. Follow the existing naming pattern
2. Include detailed docstrings explaining what the example does
3. Add proper error handling and logging
4. Update this README with information about your example 