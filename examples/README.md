# HiramAbiff Examples

This directory contains example scripts that demonstrate how to use various components of the HiramAbiff system.

## Available Examples

### DeFi Agent Example

The `defi_agent_example.py` script demonstrates how to use the DeFi agent to fetch and analyze DeFi opportunities across multiple blockchains, with a focus on Solana.

#### What it demonstrates:

- Initializing the DeFi agent with custom parameters
- Fetching yield opportunities from DeFiLlama
- Filtering opportunities based on yield and TVL thresholds
- Analyzing all chains and focusing on specific chains (Solana)
- Processing and displaying the results

#### Running the example:

```bash
# Make sure you're in the project root directory
cd /path/to/HiramAbiff

# Activate your virtual environment (if using one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the example
python examples/defi_agent_example.py
```

### Agent Collaboration Example

The `agent_collaboration_example.py` script demonstrates how multiple specialized agents can work together in the HiramAbiff system, with the DeFi agent finding opportunities and the Trading agent executing trades.

#### What it demonstrates:

- Creating and configuring multiple specialized agents
- Orchestrating agent workflows where output from one agent is used as input for another
- Error handling and resource cleanup in multi-agent systems
- Trade execution and status monitoring
- Generating comprehensive reports from agent activities

#### Running the example:

```bash
# Make sure you're in the project root directory
cd /path/to/HiramAbiff

# Activate your virtual environment (if using one)
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the example
python examples/agent_collaboration_example.py
```

## Setting Up for Examples

Before running the examples, make sure:

1. You have installed all the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. You have set up the environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

3. You have a reliable internet connection (examples make API calls to DeFiLlama and blockchain nodes)

## Troubleshooting

If you encounter issues running the examples:

- Check your API keys in the `.env` file
- Ensure you have activated your virtual environment
- Verify your internet connection
- Check the logs (usually in the `logs` directory) 