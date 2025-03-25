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
- **Alchemy Integration**: Direct access to Solana blockchain data via Alchemy's robust APIs
- **Yield Farming Dashboard**: Interactive dashboard for exploring yield opportunities and portfolio simulation
- **Risk Assessment**: Smart scoring system for evaluating yield farming risks and rewards

## New Features: Wallet Integration and Monetization

HiramAbiff now includes wallet integration and monetization features in the MVP expansion:

### Wallet Integration

The platform now supports connection to Solana wallets, including:
- Phantom wallet integration
- Solflare wallet integration
- Portfolio tracking and visualization
- Transaction history viewing
- Staked assets monitoring

To use the wallet integration:
1. Launch the yield dashboard
2. Go to the "Wallet Integration" tab
3. Click "Connect Phantom" or "Connect Solflare"
4. Your wallet data will be displayed, including portfolio, staked assets, and transaction history

Note: The current implementation uses mock data for demonstration purposes. In production, it will connect to actual wallets and fetch real data from the blockchain.

### Monetization Features

The platform includes a monetization strategy with fee management:
- Fee calculation based on profit (1% of profit by default)
- HIRAM token staking for fee discounts
- Tiered fee discount system based on staking amount
- Fee statistics and tracking

To test the monetization features:
1. Connect your wallet (mock)
2. View your fee statistics in the "Fee Information" card
3. Stake HIRAM tokens to get fee discounts
4. Simulate transactions to see how fees are calculated

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
│   │   ├── solana_client.py  # Solana blockchain client 
│   │   └── wallet.py        # Wallet management for multiple chains
│   ├── core/            # Core utilities
│   ├── data/            # Data management
│   ├── services/        # Service integrations
│   │   ├── market_data.py   # Cryptocurrency market data service
│   │   └── ai_analysis.py   # AI-powered market analysis
│   ├── web/             # Web dashboard and API
│   ├── data_aggregator.py      # Yield data aggregation
│   ├── opportunity_detector.py # Yield opportunity detection
│   ├── trade_simulator.py      # Yield strategy simulation
│   ├── yield_insights.py       # AI-powered yield analysis
│   └── yield_dashboard.py      # Yield farming dashboard
├── tests/               # Tests
├── tools/               # Development tools
├── .env.example         # Example environment variables
├── CONTRIBUTING.md      # Contribution guidelines
├── LICENSE              # License information
├── NEXT_STEPS.md        # Future roadmap
├── PROJECT_SUMMARY.md   # Project summary and roadmap
├── README.md            # This file
├── run_yield_dashboard.py # Yield dashboard entry point
├── requirements.txt     # Production dependencies
├── simple_dashboard.py  # Main dashboard application
├── test_alchemy_integration.py # Alchemy API integration test
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

5. Set up required API keys:
   - **OpenAI API Key**: For AI-powered market analysis
   - **Alchemy API Key**: For enhanced Solana blockchain access
   - **Solana RPC URL**: For direct blockchain data access

6. Verify your setup with the dependency checker:
   ```bash
   python tools/check_dependencies.py
   ```

### Quick Start

Run the dashboard application:

```bash
python simple_dashboard.py
```

This will start the HiramAbiff Dashboard at http://localhost:8890/dashboard/

The dashboard features:
- Real-time market data for top 15 cryptocurrencies
- Solana network statistics (TPS, latest slot)
- Price history charts and price change comparisons
- Market cap distribution visualization
- AI-powered market analysis reports (requires OpenAI API key)
- Auto-refresh functionality that updates data every 5 minutes

Run the yield farming dashboard:

```bash
python run_yield_dashboard.py
```

This will start the Yield Farming Dashboard at http://localhost:8889/

The yield dashboard features:
- Real-time yield farming opportunities from Solana DeFi protocols
- Risk assessment and opportunity scoring
- Portfolio simulation with various compounding strategies
- AI-powered yield analysis and recommendations
- Interactive filtering and visualization

You can also test the Alchemy API integration:

```bash
python test_alchemy_integration.py
```

For other functionality, use the command-line interface:

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
- [Alchemy Integration](docs/ALCHEMY_INTEGRATION.md): Guide to using Alchemy's Solana APIs
- [Yield Farming](yield_README.md): Guide to using the yield farming dashboard

## Alchemy Integration

HiramAbiff now features robust integration with Alchemy's Solana API, providing several benefits:

- **Enhanced Reliability**: Access to Solana's blockchain with industry-leading uptime
- **Performance**: Faster RPC responses compared to public endpoints
- **Advanced Features**: Access to Alchemy-specific enhanced APIs
- **Reduced Rate Limiting**: Higher rate limits for production applications

To use the Alchemy integration:

1. Sign up for an Alchemy account at [alchemy.com](https://www.alchemy.com/)
2. Create a Solana app in the Alchemy dashboard
3. Copy your API key and Solana URL to your `.env` file:
   ```
   ALCHEMY_API_KEY=your_api_key_here
   ALCHEMY_SOLANA_URL=https://solana-mainnet.g.alchemy.com/v2/your_api_key_here
   ```

Test your integration with:
```bash
python test_alchemy_integration.py
```

## Development

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Roadmap

For future plans and development roadmap, see [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Alchemy for their powerful blockchain infrastructure
- DeFi Llama for their comprehensive DeFi data
- CoinGecko for their token pricing API
- OpenAI for their powerful language models
- The Solana and Ethereum communities for their extensive documentation and tools 

## Running the Demo

To run the full HiramAbiff platform demo:

```bash
# Start both dashboards with one command
./demo.py

# Run only the yield dashboard with wallet features
./demo.py --yield-only

# Run in debug mode
./demo.py --debug

# Don't automatically open browsers
./demo.py --no-browser
```

The demo will start both dashboards:
- Market Dashboard: http://localhost:8890/
- Yield Dashboard: http://localhost:8889/ 