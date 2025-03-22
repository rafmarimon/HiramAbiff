# Token Tracking and Analysis in HiramAbiff

This document provides information about the token tracking and analysis features in HiramAbiff, including how to use the CLI commands, understand the data, and leverage LLM-powered insights.

## Overview

HiramAbiff's token tracking module allows you to:

1. Track cryptocurrency prices and market data in real-time
2. Analyze historical token performance with key statistical metrics
3. Monitor wallet balances across multiple blockchains
4. Generate portfolio analysis with asset distribution
5. Leverage OpenAI's LLMs for intelligent insights and investment strategies

## Prerequisites

- Python 3.8+ installed
- HiramAbiff package installed (`pip install -e .` from project root)
- API keys configured in `.env` file:
  - `ETHERSCAN_API_KEY`: For Ethereum blockchain data
  - `OPENAI_API_KEY`: For LLM-powered analysis
  - `ALCHEMY_API_KEY`: For additional Ethereum data (optional)
  - `INFURA_API_KEY`: For Ethereum node access (optional)

## CLI Commands

### Get Token Price

```bash
hiramabiff token price BTC
```

This retrieves the current price and market data for a token, including:
- Current price in USD
- Market capitalization
- 24-hour trading volume
- 24-hour price change percentage

**Parameters:**
- `symbol`: Token symbol (e.g., BTC, ETH, SOL)

### Analyze Token

```bash
hiramabiff token analyze ETH
```

For deeper analysis, including historical performance metrics:

```bash
hiramabiff token analyze ETH --llm
```

This command performs statistical analysis on token data and provides:
- Current price and market metrics
- 30-day statistics (mean, min, max, volatility)
- 7-day and 24-hour price changes
- With `--llm` flag, AI-generated insights about the token's performance and outlook

**Parameters:**
- `symbol`: Token symbol (e.g., BTC, ETH, SOL)
- `--llm`: (Optional) Generate LLM-powered analysis

### Portfolio Analysis

```bash
hiramabiff token portfolio ethereum:0x123abc... solana:AbCdEf123...
```

With LLM-powered insights:

```bash
hiramabiff token portfolio ethereum:0x123abc... solana:AbCdEf123... --llm
```

This analyzes balances across multiple blockchain wallets to provide:
- Total portfolio value in USD
- Token distribution and percentages
- With `--llm` flag, AI-generated portfolio assessment including diversification, risk, and allocation recommendations

**Parameters:**
- `wallets`: One or more wallet addresses in format `chain:address`
- `--llm`: (Optional) Generate LLM-powered portfolio report

### Market Analysis

```bash
hiramabiff llm market
```

Save to file:

```bash
hiramabiff llm market --output market_report.md
```

This command uses LLMs to generate a comprehensive analysis of the current cryptocurrency market, including:
- Performance of major cryptocurrencies
- Sector trends (DeFi, NFTs, etc.)
- Technical indicators and sentiment
- Macroeconomic factors and regulatory developments
- Market outlook and trends

**Parameters:**
- `--output`, `-o`: (Optional) Save the analysis to a markdown file

### DeFi Investment Strategy

```bash
hiramabiff llm strategy --risk-profile moderate --amount 5000
```

This generates an AI-powered investment strategy for DeFi opportunities:
- Fetches current yield opportunities across specified blockchains
- Creates a customized allocation strategy based on risk profile
- Provides detailed rationale for each allocation
- Includes risk mitigation approaches and monitoring recommendations

**Parameters:**
- `--chains`, `-c`: Chains to include (default: Solana, Ethereum)
- `--risk-profile`, `-r`: Risk tolerance (conservative, moderate, aggressive)
- `--amount`, `-a`: Investment amount in USD
- `--min-yield`, `-y`: Minimum yield percentage to consider
- `--min-tvl`, `-t`: Minimum Total Value Locked (TVL) to consider
- `--max-opportunities`, `-m`: Maximum number of opportunities to include
- `--output`, `-o`: (Optional) Save the strategy to a markdown file

## Data Storage

HiramAbiff stores data in the following locations:

- Token data: `~/.hiramabiff/data/tokens/`
- Analysis reports: `~/.hiramabiff/reports/`
- Wallets: `~/.hiramabiff/wallets/`

## API Integration

The token tracking module integrates with:

1. CoinGecko API for price and market data
2. Etherscan API for Ethereum wallet data
3. Solana RPC API for Solana wallet data
4. OpenAI API for LLM-powered analysis

## Examples

### Basic Token Analysis Workflow

```bash
# Check Bitcoin's current price
hiramabiff token price BTC

# Analyze Ethereum with AI insights
hiramabiff token analyze ETH --llm

# Get a market overview
hiramabiff llm market

# Generate a DeFi strategy
hiramabiff llm strategy --risk-profile conservative --amount 10000
```

### Portfolio Management Workflow

```bash
# Create a wallet
hiramabiff wallet create ethereum my_eth_wallet

# Import an existing wallet
hiramabiff wallet import solana my_sol_wallet 5xJdqKNv...

# Check wallet balance
hiramabiff wallet balance my_eth_wallet

# Analyze your portfolio
hiramabiff token portfolio ethereum:0x123... solana:ABC... --llm
```

## Extending the Module

The token tracking module can be extended programmatically:

```python
from hiramabiff.analysis import TokenTracker, LLMAnalyzer

# Initialize the token tracker
tracker = TokenTracker()

# Get token price
async def get_price():
    btc_data = await tracker.get_token_price("BTC")
    print(f"Bitcoin price: ${btc_data['price_usd']}")

# Analyze a token
async def analyze():
    analysis = await tracker.analyze_token("ETH")
    print(f"Ethereum volatility: {analysis['stats']['volatility_30d']}")

# Initialize the LLM analyzer
llm = LLMAnalyzer()

# Generate market analysis
async def market_analysis():
    report = await llm.analyze_market_trend()
    print(report["llm_analysis"]["text"])
```

## Troubleshooting

If you encounter issues:

1. Ensure your API keys are correctly set in the `.env` file
2. Check your internet connection
3. Verify the token symbols are valid
4. For wallet analysis, ensure addresses are correctly formatted
5. If LLM analysis fails, check your OpenAI API key and quota

For more help, run commands with the `--verbose` flag for detailed logging. 