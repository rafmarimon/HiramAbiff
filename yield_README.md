# HiramAbiff Yield Farming Dashboard

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This component of HiramAbiff focuses on optimizing yield farming strategies using data from DeFi Llama, portfolio simulation, and AI-powered insights.

![Dashboard Preview](dashboard_preview.png)

## Features

- **Real-time Yield Data**: Fetches and displays current yield farming opportunities from Solana DeFi protocols via DeFi Llama's API
- **Intelligent Opportunity Detection**: Ranks and filters yield opportunities using customizable criteria
- **Risk Assessment**: Evaluates opportunities based on protocol reputation, TVL, and APY factors
- **Portfolio Simulation**: Simulates investment returns with various compounding strategies
- **AI-Powered Insights**: Uses OpenAI to generate concise analysis of opportunities and portfolios
- **Caching System**: Minimizes API calls with intelligent local caching
- **Interactive Dashboard**: Clean, intuitive Dash-based UI for exploring opportunities

## Components

- **Data Aggregator**: `src/data_aggregator.py` - Fetches yield data from DeFi Llama with efficient caching
- **Opportunity Detector**: `src/opportunity_detector.py` - Analyzes and ranks yield opportunities
- **Trade Simulator**: `src/trade_simulator.py` - Simulates yield strategies without real transactions
- **Yield Insights**: `src/yield_insights.py` - Provides AI analysis with OpenAI integration
- **Yield Dashboard**: `src/yield_dashboard.py` - Interactive Dash dashboard for visualizing data

## Getting Started

### Prerequisites

- Python 3.8+ (Python 3.10+ recommended)
- Required Python packages (see `requirements.txt`)
- (Optional) OpenAI API key for AI-powered insights

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

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Add your OpenAI API key to a `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   ```

### Running the Dashboard

Start the yield dashboard with:

```bash
python run_yield_dashboard.py
```

Available options:
- `--port 8889` - Change the port (default: 8889)
- `--debug` - Run in debug mode
- `--demo` - Initialize with a demo portfolio

### Data Sources

- **DeFi Llama API**: Fetch yield farming opportunities from Solana DeFi protocols
- No authentication required for basic API access
- Free to use within rate limits

## Dashboard Features

### Yield Opportunities

The dashboard displays yield farming opportunities with:
- Current APY
- Total Value Locked (TVL)
- Risk assessment (Low, Medium, High, Very High)
- Opportunity score combining risk and reward
- Protocol and pool information

### Filtering Options

Filter opportunities by:
- Minimum APY threshold
- Minimum TVL requirement
- Risk levels
- Specific protocols (Raydium, Orca, Marinade, etc.)

### Portfolio Management

- View current portfolio allocation
- See expected returns over time
- Track weighted APY across strategies
- View detailed strategy breakdown

### AI-Powered Analysis

With a valid OpenAI API key, the dashboard provides:
- Summarized market analysis for top opportunities
- Portfolio assessment and recommendations
- Risk-reward evaluations
- Investment suggestions

## Using Without External APIs

For testing without external APIs, the system includes:
- Simulated yield data for major Solana protocols
- Mock portfolio tracking
- Fallback sample AI insights when no API key is available

## Development

### Directory Structure

```
HiramAbiff/
├── src/
│   ├── data_aggregator.py     # Fetches yield data from DeFi Llama
│   ├── opportunity_detector.py # Analyzes and ranks opportunities
│   ├── trade_simulator.py     # Simulates yield strategies
│   ├── yield_insights.py      # AI-powered analysis with OpenAI
│   └── yield_dashboard.py     # Dash dashboard interface
├── run_yield_dashboard.py     # Entry point script
├── cache/                     # Cached data
├── portfolios/                # Saved portfolio data
├── assets/                    # Dashboard assets
└── yield_README.md            # This documentation
```

### Extending the System

- **Adding new protocols**: Extend the `solana_specific_urls` dictionary in `data_aggregator.py`
- **Modifying risk assessment**: Adjust the logic in `calculate_risk_score` method in `opportunity_detector.py`
- **Customizing AI prompts**: Edit the prompt templates in `yield_insights.py`

## Cost Efficiency

This dashboard is designed to minimize costs:
- Local caching of DeFi Llama data to reduce API calls
- Limited, efficient OpenAI API usage with reasonable token limits
- Simulated portfolio tracking without blockchain transactions
- Everything runs locally without external hosting costs

## Roadmap

- Add real wallet integration for tracking actual holdings
- Expand to additional blockchains (Ethereum, Arbitrum, etc.)
- Implement historical yield data analysis
- Add direct trading capabilities through DEX APIs

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- DeFi Llama for their comprehensive yield data
- OpenAI for their API services
- The Solana ecosystem and its DeFi protocols 