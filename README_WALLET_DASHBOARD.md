# HiramAbiff Enhanced Yield Dashboard

This enhanced yield dashboard provides a comprehensive interface for monitoring and managing yield farming opportunities on Solana, with wallet integration and fee management capabilities.

## Features

- **Data Aggregation**: Fetch and display yield data from DeFi Llama API
- **Opportunity Detection**: Rank and analyze yield opportunities based on APY, TVL, and risk
- **Mock Wallet Integration**: Connect to Phantom/Solflare wallets (mock implementation)
- **Portfolio Tracking**: Track and manage your yield farming strategies
- **AI-Powered Insights**: Generate analysis of opportunities using OpenAI API
- **Fee Management**: Simulate fee calculations based on profits
- **Responsive UI**: Clean, modern interface with dark mode support

## Setup and Installation

### Prerequisites

- Python 3.8+
- Flask
- Required Python packages (see below)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/HiramAbiff.git
   cd HiramAbiff
   ```

2. Install required packages:
   ```
   pip install flask requests pandas numpy
   ```

3. (Optional) Install OpenAI for AI insights:
   ```
   pip install openai
   ```

4. Set your OpenAI API key (optional):
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Running the Dashboard

Run the enhanced dashboard with:

```
python run_yield_dashboard_enhanced.py --demo
```

Command line options:
- `--host`: Specify the host to run on (default: 0.0.0.0)
- `--port`: Specify the port (default: 8889)
- `--debug`: Enable debug mode
- `--demo`: Initialize with mock portfolio data

### Accessing the Dashboard

Open your browser and navigate to:
```
http://localhost:8889/
```

## Directory Structure

```
├── src/
│   ├── agent/
│   │   └── llm_agent.py          # AI insights integration
│   ├── blockchain/
│   │   ├── wallet.py             # Wallet management
│   │   ├── wallet_integration.py # Wallet connection interface
│   │   └── solana_client.py      # Solana blockchain client
│   ├── monetization/
│   │   └── fee_manager.py        # Fee calculation and management
│   ├── data_aggregator.py        # Fetch and cache yield data
│   ├── opportunity_detector.py   # Analyze yield opportunities
│   └── trade_simulator.py        # Simulate trading strategies
├── static/
│   ├── css/
│   │   └── styles.css            # Dashboard styling
│   └── js/
│       └── wallet_connector.js   # Wallet connection script
├── templates/
│   └── dashboard.html            # Dashboard template
├── portfolios/                   # Portfolio storage
├── cache/                        # Data and API caching
├── run_yield_dashboard_enhanced.py # Enhanced dashboard runner
└── README_WALLET_DASHBOARD.md    # This README
```

## Technical Details

### Mock Wallet Integration

The wallet integration currently uses mock data for development purposes. In the future, this will be replaced with actual blockchain interactions.

- `wallet_integration.py` - Interface for connecting to wallets
- `wallet.py` - Wallet management utilities
- `solana_client.py` - Mock Solana client for simulated blockchain data

### Data Aggregation

The dashboard fetches yield data from DeFi Llama API with caching to minimize API calls:

- `data_aggregator.py` - Fetches and processes yield data
- `cache/` - Stores cached API responses

### Opportunity Detection

Yield opportunities are analyzed and ranked based on:

- APY (Annual Percentage Yield)
- TVL (Total Value Locked)
- Risk assessment (based on protocol reputation, TVL, and other factors)

### Fee Management

The fee management system simulates fee calculations:

- Base fee: 1% of profits
- Tiered fee discounts based on token staking
- Mock staking mechanism

### AI-Powered Insights

The LLM agent provides insights using the OpenAI API:

- Analysis of top yield opportunities
- Portfolio optimization advice
- Market trend summaries

## Troubleshooting

### Dashboard Not Loading

Verify that port 8889 is not in use by another application:
```
lsof -i :8889
```

### Missing OpenAI API Key

If you see an error about missing API key:
```
export OPENAI_API_KEY=your_api_key_here
```

### Data Not Refreshing

The dashboard caches data to minimize API calls. To force a refresh, click the "Refresh Data" button or restart with the `--debug` flag.

## Future Enhancements

1. Real blockchain integration with Solana Web3.js
2. Live transaction capabilities
3. Historical performance tracking
4. Advanced portfolio analytics
5. Multi-chain support 