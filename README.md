# HiramAbiff

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Chain-agnostic DeFi agent with a focus on Solana

HiramAbiff is an intelligent multi-agent system designed to analyze and execute DeFi opportunities across multiple blockchains, with a particular focus on the Solana ecosystem. The project leverages data aggregation from services like DeFi Llama to identify optimal yields and trading strategies, and includes powerful token tracking and visualization capabilities.

## Features

- **Chain-agnostic Architecture**: Works across multiple blockchains with a focus on Solana
- **Multi-agent Collaboration**: Specialized agents work together to achieve complex tasks
- **Data Aggregation**: Fetches and analyzes data from DeFi Llama and other sources
- **Opportunity Detection**: Identifies high-yield opportunities based on customizable criteria
- **Simulated Trade Execution**: Safely tests strategies before committing real funds
- **Token Tracking & Analysis**: Tracks token prices, portfolio performance, and generates insights
- **Data Visualization**: Creates beautiful charts and graphs for token analysis and comparison
- **LLM-Powered Insights**: Uses large language models to generate investment analyses
- **Extensible Framework**: Easily add new agents, data sources, and execution methods

## Project Structure

```
HiramAbiff/
├── docs/                # Documentation
├── examples/            # Example scripts
├── scripts/             # Utility scripts
├── src/                 # Source code
│   ├── agents/          # Agent implementations
│   ├── analysis/        # Token analysis and visualization
│   ├── blockchain/      # Blockchain connectors
│   ├── core/            # Core utilities
│   ├── data/            # Data management
│   └── api/             # API interfaces
├── tests/               # Tests
├── tools/               # Development tools
├── .env.example         # Example environment variables
├── CONTRIBUTING.md      # Contribution guidelines
├── LICENSE              # License information
├── NEXT_STEPS.md        # Future roadmap
├── README.md            # This file
├── requirements.txt     # Production dependencies
└── requirements-dev.txt # Development dependencies
```

## Getting Started

### Prerequisites

- Python 3.8 or higher (Python 3.10+ recommended)
- Git
- Solana CLI tools (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/HiramAbiff.git
   cd HiramAbiff
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Set up environment variables by copying the example file:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file to add your own API keys and settings.

5. Verify your setup with the dependency checker:
   ```bash
   python tools/check_dependencies.py
   ```

### Quick Start

Run the minimal DeFi agent example:

```bash
python examples/minimal_defi_agent.py
```

This will simulate fetching and analyzing yield farming opportunities across different blockchains.

You can also use the command-line interface:

```bash
# Find yield opportunities
hiramabiff yield --chains Solana Ethereum --min-yield 10

# Check token price
hiramabiff token price BTC

# Analyze a token with chart generation
hiramabiff token analyze ETH --chart

# Compare multiple tokens
hiramabiff token compare BTC ETH SOL --normalized

# Analyze a portfolio
hiramabiff token portfolio ethereum:0x123... solana:abc... --chart

# Generate market analysis using LLM
hiramabiff llm market

# Get help
hiramabiff --help
```

For more examples, see the [examples directory](examples/).

## Documentation

### Specialized Guides

- [Token Tracking and Analysis](docs/TOKEN_TRACKING.md): Guide to tracking and analyzing tokens
- [Data Visualization](docs/VISUALIZATION.md): Guide to creating charts and graphs
- [LLM Analysis](docs/LLM_ANALYSIS.md): Guide to using LLM-powered insights
- [CLI Reference](docs/CLI_REFERENCE.md): Detailed CLI command reference

## Development

### Project Structure

```
HiramAbiff/
├── docs/                # Documentation
├── examples/            # Example scripts
├── scripts/             # Utility scripts
├── src/                 # Source code
│   ├── agents/          # Agent implementations
│   ├── analysis/        # Token analysis and visualization
│   ├── blockchain/      # Blockchain connectors
│   ├── core/            # Core utilities
│   ├── data/            # Data management
│   └── api/             # API interfaces
├── tests/               # Tests
├── tools/               # Development tools
├── .env.example         # Example environment variables
├── CONTRIBUTING.md      # Contribution guidelines
├── LICENSE              # License information
├── NEXT_STEPS.md        # Future roadmap
├── README.md            # This file
├── requirements.txt     # Production dependencies
└── requirements-dev.txt # Development dependencies
```

### Development Tools

- **Dependency Checker**: Check if your environment is set up correctly.
  ```bash
  python tools/check_dependencies.py
  ```

- **Development Dependencies**: Install development dependencies for contributing.
  ```bash
  pip install -r requirements-dev.txt
  ```

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Roadmap

For future plans and development roadmap, see [NEXT_STEPS.md](NEXT_STEPS.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- DeFi Llama for their comprehensive DeFi data
- CoinGecko for their token pricing API
- OpenAI for their powerful language models
- The Solana and Ethereum communities for their extensive documentation and tools 