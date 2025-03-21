# HiramAbiff

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Chain-agnostic DeFi agent with a focus on Solana

HiramAbiff is an intelligent multi-agent system designed to analyze and execute DeFi opportunities across multiple blockchains, with a particular focus on the Solana ecosystem. The project leverages data aggregation from services like DeFi Llama to identify optimal yields and trading strategies.

## Features

- **Chain-agnostic Architecture**: Works across multiple blockchains with a focus on Solana
- **Multi-agent Collaboration**: Specialized agents work together to achieve complex tasks
- **Data Aggregation**: Fetches and analyzes data from DeFi Llama and other sources
- **Opportunity Detection**: Identifies high-yield opportunities based on customizable criteria
- **Simulated Trade Execution**: Safely tests strategies before committing real funds
- **Extensible Framework**: Easily add new agents, data sources, and execution methods

## Project Structure

```
HiramAbiff/
├── examples/                # Example scripts demonstrating usage
├── src/
│   ├── agents/             # Agent implementations
│   │   ├── base_agent.py   # Base agent class
│   │   ├── defi_agent.py   # DeFi opportunity finder
│   │   └── trading_agent.py # Trade execution agent
│   ├── blockchain/         # Blockchain connectivity
│   │   └── solana_client.py # Solana client implementation
│   ├── core/               # Core functionality
│   │   ├── config.py       # Configuration handling
│   │   └── logger.py       # Logging setup
│   ├── data/               # Data sources
│   │   └── defillama.py    # DeFi Llama integration
│   └── app.py              # Main application entry point
├── .env.example            # Example environment variables
├── .gitignore              # Git ignore file
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── requirements.txt        # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.9+
- Pip package manager
- Git

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/rafmarimon/HiramAbiff.git
   cd HiramAbiff
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

### Running Examples

Check out the examples directory for ready-to-run demonstrations:

```bash
# Run the DeFi agent example
python examples/defi_agent_example.py

# Run the agent collaboration example
python examples/agent_collaboration_example.py
```

## Development

### Adding a New Agent

1. Create a new agent class that extends `BaseAgent`
2. Implement the required methods, especially `run()`
3. Add any agent-specific functionality
4. See `defi_agent.py` and `trading_agent.py` for examples

### Adding New Data Sources

1. Create a new module in the `data` directory
2. Implement methods to fetch and process data
3. Update existing agents or create new ones to utilize the data

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- DeFi Llama for their comprehensive DeFi data
- The Solana community for their extensive documentation and tools 