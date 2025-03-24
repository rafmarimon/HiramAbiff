#!/usr/bin/env python
"""
Simple HiramAbiff Dashboard

A standalone dashboard without dependencies on complex components.
"""

import datetime
import os
import sys
import argparse
from pathlib import Path
import json
from dotenv import load_dotenv
import requests
import time

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

# Load environment variables
load_dotenv()

# Get Alchemy API settings
ALCHEMY_API_KEY = os.getenv("ALCHEMY_API_KEY", "")
ALCHEMY_SOLANA_URL = f"https://solana-mainnet.g.alchemy.com/v2/{ALCHEMY_API_KEY}"
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", "8888"))

# If we have an Alchemy Solana URL, log it (but mask the API key for security)
if ALCHEMY_SOLANA_URL:
    base_url = ALCHEMY_SOLANA_URL.split('/v2/')[0]
    print(f"Using Alchemy Solana API: {base_url}/v2/...")
else:
    print("Alchemy Solana API not configured. Using mock data.")

# Add function to fetch Solana data from Alchemy
def fetch_solana_network_data():
    """Fetch Solana network data from Alchemy API."""
    if not ALCHEMY_SOLANA_URL:
        print("Alchemy Solana API not configured. Cannot fetch Solana network data.")
        return None
    
    try:
        print("Fetching Solana network data from Alchemy...")
        
        # JSON-RPC request to get recent blockhash
        headers = {
            "Content-Type": "application/json"
        }
        
        network_data = {}
        
        # Get recent performance samples
        payload = {
            "id": 1,
            "jsonrpc": "2.0",
            "method": "getRecentPerformanceSamples",
            "params": [4]  # Get last 4 samples
        }
        
        response = requests.post(ALCHEMY_SOLANA_URL, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json().get('result', [])
            if result:
                # Calculate average TPS
                avg_tps = sum(sample.get('numTransactions', 0) / sample.get('samplePeriodSecs', 1) for sample in result) / len(result)
                network_data["tps"] = round(avg_tps, 2)
                
                # Get slot information
                slot_payload = {
                    "id": 2,
                    "jsonrpc": "2.0",
                    "method": "getSlot",
                    "params": []
                }
                slot_response = requests.post(ALCHEMY_SOLANA_URL, headers=headers, json=slot_payload, timeout=10)
                network_data["current_slot"] = slot_response.json().get('result', 0) if slot_response.status_code == 200 else 0
                
                # Get validator count
                validators_payload = {
                    "id": 3,
                    "jsonrpc": "2.0",
                    "method": "getVoteAccounts",
                    "params": []
                }
                validators_response = requests.post(ALCHEMY_SOLANA_URL, headers=headers, json=validators_payload, timeout=10)
                if validators_response.status_code == 200:
                    validator_result = validators_response.json().get('result', {})
                    current_validators = len(validator_result.get('current', []))
                    delinquent_validators = len(validator_result.get('delinquent', []))
                    network_data["validators"] = {
                        "active": current_validators,
                        "delinquent": delinquent_validators,
                        "total": current_validators + delinquent_validators
                    }
                
                # Get blockchain supply info
                supply_payload = {
                    "id": 4,
                    "jsonrpc": "2.0",
                    "method": "getSupply",
                    "params": []
                }
                supply_response = requests.post(ALCHEMY_SOLANA_URL, headers=headers, json=supply_payload, timeout=10)
                if supply_response.status_code == 200:
                    supply_result = supply_response.json().get('result', {}).get('value', {})
                    network_data["supply"] = {
                        "total": float(supply_result.get('total', 0)) / 1_000_000_000,  # Convert to billions SOL
                        "circulating": float(supply_result.get('circulating', 0)) / 1_000_000_000
                    }
                
                # Try to get recent block time
                time_payload = {
                    "id": 5,
                    "jsonrpc": "2.0",
                    "method": "getBlockTime",
                    "params": [network_data["current_slot"]]
                }
                time_response = requests.post(ALCHEMY_SOLANA_URL, headers=headers, json=time_payload, timeout=10)
                if time_response.status_code == 200:
                    block_time = time_response.json().get('result')
                    if block_time:
                        network_data["block_time"] = block_time
                        # Calculate time since last block
                        current_time = int(time.time())
                        network_data["block_time_diff"] = current_time - block_time
                
                return network_data
        
        print("Failed to fetch Solana network data from Alchemy")
        return None
    except Exception as e:
        print(f"Error fetching Solana network data: {str(e)}")
        return None

# Sample report for when API is unavailable
sample_report = {
    "content": """# Market Overview
The cryptocurrency market is showing mixed signals with Bitcoin maintaining dominance at approximately 48% of total market cap. Overall capitalization stands at approximately $2.5 trillion.

# Key Observations
Bitcoin continues consolidation near the $65,000 level, while Ethereum shows strength with reduced selling pressure. Altcoins display variable performance with Solana leading in 24-hour gains.

# Technical Analysis
BTC has established strong support at $62,000 with resistance at $68,500. ETH shows a bullish pattern with resistance at $3,600 and support strengthening at $3,200.

# Market Predictions
Short-term outlook suggests continued range-bound trading for Bitcoin between $62K-$68K, while ETH could test $3,800 if market sentiment remains positive.

# Investment Opportunities
Mid-cap altcoins present attractive risk-reward ratios, particularly in the DeFi and AI token sectors. Consider accumulation during market dips.

# DeFi Trends
The total value locked (TVL) in DeFi protocols has increased by 12% over the past month, with growth primarily driven by liquid staking derivatives and real-world asset protocols.

# Traditional Market Comparison
Crypto correlation with tech stocks has weakened in recent weeks, suggesting a potential decoupling. Gold continues to move inversely to Bitcoin on a macro scale.""",
    "market_sentiment": "neutral",
    "bitcoin_dominance": 48.5,
    "total_market_cap": 2.5,
    "timestamp": datetime.datetime.now().isoformat()
}

# Function to generate market analysis reports using OpenAI
def generate_market_analysis(assets_data):
    """Generate market analysis reports using OpenAI API."""
    try:
        from openai import OpenAI
        
        # Get OpenAI API key from environment
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print("OpenAI API key not found. Using sample analysis.")
            return sample_report
        
        print("Generating market analysis using OpenAI...")
        
        # Create OpenAI client
        client = OpenAI(api_key=openai_api_key)
        
        # Format asset data for the prompt, including historical changes
        market_data = "\n".join([
            f"{asset['name']} ({asset['symbol']}): "
            f"${asset['price']:,.2f}, "
            f"24h: {asset['change']:+.2f}%, "
            f"7d: {asset.get('change_7d', 0):+.2f}%, "
            f"30d: {asset.get('change_30d', 0):+.2f}%, "
            f"ATH: ${asset.get('ath', 0):,.2f} ({asset.get('ath_change_percentage', 0):+.2f}% from peak), "
            f"Market Cap: ${asset['marketCap']}T (#Rank {asset.get('market_cap_rank', 'N/A')}), "
            f"Volume: ${asset['volume']}B"
            for asset in assets_data
        ])
        
        # Get general market sentiment indicators
        bitcoin_dominance = 0
        total_market_cap = 0
        for asset in assets_data:
            total_market_cap += asset['marketCap']
            if asset['symbol'] == 'BTC':
                bitcoin_dominance = (asset['marketCap'] / total_market_cap) * 100 if total_market_cap > 0 else 0
        
        # Check if market is generally bullish or bearish in the last 24h
        positive_assets = sum(1 for asset in assets_data if asset['change'] > 0)
        negative_assets = sum(1 for asset in assets_data if asset['change'] < 0)
        market_sentiment = "bullish" if positive_assets > negative_assets else "bearish" if negative_assets > positive_assets else "neutral"
        
        # Get traditional market data (this would normally come from an API)
        traditional_markets = {
            "S&P 500": {"value": 5432.10, "change": 0.8},
            "Gold": {"value": 2345.67, "change": 0.3},
            "USD Index": {"value": 101.23, "change": -0.4}
        }
        
        traditional_market_data = "\n".join([
            f"{name}: ${data['value']:,.2f}, Change: {data['change']:+.2f}%"
            for name, data in traditional_markets.items()
        ])
        
        # Create the prompt for OpenAI with market context
        prompt = f"""Based on the following cryptocurrency market data, provide a comprehensive market analysis report:

{market_data}

Market Context:
- Overall market sentiment in the last 24 hours: {market_sentiment}
- Bitcoin dominance: {bitcoin_dominance:.2f}%
- Total market cap of top cryptocurrencies: ${total_market_cap:.2f}T

Traditional Market Data:
{traditional_market_data}

Include:
1. Market Overview - current state of the crypto market with key metrics
2. Key Observations - notable trends or patterns across multiple timeframes (24h, 7d, 30d)
3. Technical Analysis - support/resistance levels and market structure for Bitcoin and Ethereum
4. Market Predictions - short-term outlook with potential scenarios (bullish and bearish cases)
5. Investment Opportunities - potential areas of interest with risk assessment
6. DeFi Trends - analysis of decentralized finance ecosystem and notable platforms
7. Traditional Market Comparison - brief comparison with traditional market indicators (S&P 500, Gold, USD)

Format your response with Markdown headings for each section.
"""
        
        # Call the OpenAI API with improved parameters
        response = client.chat.completions.create(
            model="gpt-4o",  # Using GPT-4o for better financial analysis
            messages=[
                {"role": "system", "content": "You are a professional cryptocurrency market analyst with expertise in technical analysis, DeFi, and traditional finance. Provide insightful and data-driven market analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        # Get the response content
        market_analysis = response.choices[0].message.content if response.choices else ""
        
        # Create the market report with the analysis
        report = {
            "content": market_analysis,
            "market_sentiment": market_sentiment,
            "bitcoin_dominance": bitcoin_dominance,
            "total_market_cap": total_market_cap,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        return report
        
    except Exception as e:
        print(f"Error generating market analysis: {str(e)}")
        print("Using sample analysis.")
        return sample_report

# Sample data for demonstration
assets = [
    {"name": "Bitcoin", "symbol": "BTC", "price": 65432.10, "change": 2.3, "volume": 28.5, "marketCap": 1.25},
    {"name": "Ethereum", "symbol": "ETH", "price": 3456.78, "change": -1.2, "volume": 12.3, "marketCap": 0.42},
    {"name": "Solana", "symbol": "SOL", "price": 123.45, "change": 5.6, "volume": 6.7, "marketCap": 0.05},
    {"name": "Cardano", "symbol": "ADA", "price": 0.48, "change": 0.8, "volume": 5.2, "marketCap": 0.02},
    {"name": "Polkadot", "symbol": "DOT", "price": 6.72, "change": -2.1, "volume": 3.1, "marketCap": 0.01},
]

# Add function to fetch real data
def fetch_real_crypto_data():
    """Fetch real cryptocurrency data from APIs."""
    try:
        print("Attempting to fetch real cryptocurrency data...")
        
        # Use CoinGecko API for general crypto data - expanded to top 15 cryptocurrencies
        response = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={
                "vs_currency": "usd",
                "ids": "bitcoin,ethereum,binancecoin,solana,xrp,cardano,dogecoin,tron,polkadot,polygon,avalanche-2,chainlink,shiba-inu,litecoin,uniswap",
                "order": "market_cap_desc",
                "per_page": 15,
                "page": 1,
                "sparkline": True,  # Get price sparkline data for the last 7 days
                "price_change_percentage": "24h,7d,30d"  # Get multiple timeframe changes
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            real_assets = []
            
            for coin in data:
                # Extract 7-day sparkline data for charts
                sparkline_prices = coin.get("sparkline_in_7d", {}).get("price", [])
                # Sample the sparkline data to reduce data size (take every 8th point = ~every 2 hours)
                sampled_prices = sparkline_prices[::8] if sparkline_prices else []
                
                real_assets.append({
                    "name": coin["name"],
                    "symbol": coin["symbol"].upper(),
                    "price": coin["current_price"],
                    "change": coin["price_change_percentage_24h"] or 0,
                    "change_7d": coin.get("price_change_percentage_7d_in_currency", 0),
                    "change_30d": coin.get("price_change_percentage_30d_in_currency", 0),
                    "volume": round(coin["total_volume"] / 1_000_000_000, 2),  # Convert to billions
                    "marketCap": round(coin["market_cap"] / 1_000_000_000_000, 3),  # Convert to trillions with more precision
                    "sparkline": sampled_prices,
                    "ath": coin.get("ath", 0),
                    "ath_change_percentage": coin.get("ath_change_percentage", 0),
                    "market_cap_rank": coin.get("market_cap_rank", 0)
                })
                
            print(f"Successfully fetched data for {len(real_assets)} cryptocurrencies")
            return real_assets
        else:
            print(f"Failed to fetch data from CoinGecko: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error fetching cryptocurrency data: {str(e)}")
        return None

# Try to get real data, fall back to sample data if unsuccessful
real_data = fetch_real_crypto_data()
if real_data:
    assets = real_data
    print("Using real cryptocurrency data for dashboard")
else:
    print("Using sample data for dashboard")

# Get Solana network data
solana_network_data = fetch_solana_network_data()
if not solana_network_data:
    # Fallback data if Solana API fails
    solana_network_data = {
        "tps": 3200,
        "current_slot": 245783401,
        "validators": {
            "active": 1500,
            "total": 1875
        },
        "supply": {
            "circulating": 556.8
        },
        "block_time_diff": 0.4
    }
    print("Using fallback Solana network data")
else:
    print(f"Using real Solana network data with TPS: {solana_network_data['tps']}")

# Generate market analysis
try:
    # If we have a valid OpenAI API key, generate a report
    if os.getenv("OPENAI_API_KEY") and os.getenv("OPENAI_API_KEY") != "your_openai_api_key_here":
        market_report = generate_market_analysis(assets)
        print("Generated market analysis report with OpenAI")
    else:
        # Otherwise, use the sample report
        market_report = sample_report
        print("Using sample market analysis (no valid OpenAI API key found)")
except Exception as e:
    print(f"Error generating report: {str(e)}")
    market_report = sample_report

# Parse the market report into sections for display
sections = []
current_section = {"title": "Summary", "content": []}

for line in market_report["content"].split('\n'):
    if line.strip() == '':
        continue
    elif line.startswith('# '):
        if current_section["content"]:
            sections.append(current_section)
        current_section = {"title": line[2:], "content": []}
    else:
        current_section["content"].append(line)

if current_section["content"]:
    sections.append(current_section)

print(f"Parsed market analysis into {len(sections)} sections")

# Create dashboard
def create_dashboard():
    """Create the Dash application with Bootstrap styling."""
    # Create Dash app with Flatly theme (dark mode)
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.DARKLY, "https://use.fontawesome.com/releases/v5.15.4/css/all.css"],
        routes_pathname_prefix="/dashboard/"
    )
    
    # Create visualizations from the data
    df = pd.DataFrame(assets)
    
    # Price chart - bar chart of current prices
    fig_price = px.bar(
        df, 
        x="symbol", 
        y="price", 
        color="change",
        color_continuous_scale=["#FF5C5C", "#F8F9FA", "#5DFDCB"],
        title="Current Asset Prices",
        labels={"symbol": "Asset", "price": "Price (USD)", "change": "24h Change (%)"},
        template="plotly_dark"
    )
    
    # Market cap chart - pie chart of market cap distribution
    fig_market_cap = px.pie(
        df,
        values='marketCap',
        names='symbol',
        title='Market Cap Distribution (in Trillions USD)',
        hole=0.6,
        template="plotly_dark"
    )
    
    # Create historical price chart for Bitcoin
    bitcoin_data = next((asset for asset in assets if asset['symbol'] == 'BTC'), None)
    ethereum_data = next((asset for asset in assets if asset['symbol'] == 'ETH'), None)
    
    # Create a basic historical chart
    fig_price_history = go.Figure()
    fig_price_history.update_layout(
        title='7-Day Price History',
        template='plotly_dark'
    )
    
    if bitcoin_data and 'sparkline' in bitcoin_data and bitcoin_data['sparkline']:
        # Create timestamps for the sparkline data (7 days worth)
        now = datetime.datetime.now()
        timestamps = [now - datetime.timedelta(days=7) + datetime.timedelta(hours=i*2) for i in range(len(bitcoin_data['sparkline']))]
        
        # Create a DataFrame for the price history
        price_history_data = []
        
        # Add Bitcoin price history
        for i, price in enumerate(bitcoin_data['sparkline']):
            price_history_data.append({
                'timestamp': timestamps[i],
                'price': price,
                'asset': 'BTC'
            })
            
        # Add Ethereum price history if available
        if ethereum_data and 'sparkline' in ethereum_data and ethereum_data['sparkline']:
            for i, price in enumerate(ethereum_data['sparkline']):
                price_history_data.append({
                    'timestamp': timestamps[i],
                    'price': price,
                    'asset': 'ETH'
                })
        
        # Create the DataFrame
        price_history_df = pd.DataFrame(price_history_data)
        
        # Create the historical price chart
        fig_price_history = px.line(
            price_history_df,
            x='timestamp',
            y='price',
            color='asset',
            title='7-Day Price History',
            template='plotly_dark',
            color_discrete_map={'BTC': '#F7931A', 'ETH': '#627EEA'}
        )
        
        fig_price_history.update_layout(
            xaxis_title='Date',
            yaxis_title='Price (USD)',
            legend_title='Asset',
            hovermode='x unified'
        )
    
    # Create price change comparison chart
    if 'change_7d' in df.columns and 'change_30d' in df.columns:
        fig_change_comparison = px.bar(
            df.sort_values('change', ascending=False),
            x='symbol',
            y=['change', 'change_7d', 'change_30d'],
            title='Price Change Comparison',
            template='plotly_dark',
            barmode='group',
            labels={
                'symbol': 'Asset',
                'value': 'Change (%)',
                'variable': 'Timeframe'
            }
        )
        fig_change_comparison.update_layout(
            legend_title='Timeframe',
            yaxis_title='Change (%)'
        )
        # Rename the legend items
        newnames = {'change': '24h', 'change_7d': '7d', 'change_30d': '30d'}
        fig_change_comparison.for_each_trace(lambda t: t.update(name=newnames[t.name]))
    else:
        fig_change_comparison = px.bar(
            df.sort_values('change', ascending=False),
            x='symbol',
            y='change',
            title='24h Price Change Comparison',
            template='plotly_dark'
        )
        fig_change_comparison.update_layout(
            yaxis_title='24h Change (%)'
        )
    
    # Format the report with cards for each section
    report_components = [
        dbc.Alert([
            html.I(className="fas fa-info-circle me-2"),
            f"Report generated on {datetime.datetime.now().strftime('%B %d, %Y at %H:%M')}",
        ], color="info", className="animate-on-scroll mb-4"),
    ]
    
    for section in sections:
        section_card = dbc.Card([
            dbc.CardHeader([
                html.H4(section["title"], className="m-0")
            ]),
            dbc.CardBody([
                html.P(paragraph, className="mb-2") for paragraph in section["content"] if paragraph.strip()
            ])
        ], className="mb-4 animate-on-scroll")
        report_components.append(section_card)
    
    # Main layout
    app.layout = html.Div([
        # Navigation
        dbc.NavbarSimple(
            brand=html.Span([
                html.I(className="fas fa-chart-line me-2"),
                "HiramAbiff Dashboard"
            ]),
            brand_href="/dashboard/",
            color="primary",
            dark=True,
            className="mb-4",
            children=[
                dbc.NavItem(dbc.NavLink(
                    html.Span([html.I(className="fas fa-home me-1"), "Overview"]), 
                    href="/dashboard/"
                )),
                dbc.NavItem(dbc.NavLink(
                    html.Span([html.I(className="fas fa-chart-bar me-1"), "Market Analysis"]), 
                    href="/dashboard/market-analysis"
                )),
                dbc.NavItem(dbc.NavLink(
                    html.Span([html.I(className="fas fa-wallet me-1"), "Wallet Info"]), 
                    href="/dashboard/wallet-info"
                )),
                dbc.NavItem(dbc.NavLink(
                    html.Span([html.I(className="fas fa-cog me-1"), "Settings"]), 
                    href="/dashboard/settings"
                )),
            ],
        ),
        
        # Auto-refresh intervals (hidden)
        html.Div([
            dcc.Interval(
                id='market-refresh-interval',
                interval=5*60*1000,  # 5 minutes in milliseconds
                n_intervals=0
            ),
            dcc.Interval(
                id='analysis-refresh-interval',
                interval=60*60*1000,  # 1 hour in milliseconds
                n_intervals=0
            ),
            # Store for market analysis data
            dcc.Store(id='market-analysis-report', data=market_report),
            dcc.Store(id='market-analysis-sections', data=sections)
        ], style={'display': 'none'}),
        
        # Content
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("HiramAbiff Dashboard", className="mb-4 animate-on-scroll"),
                    html.P("Chain-Agnostic DeFi Agent Dashboard with AI-Powered Market Analysis", className="lead animate-on-scroll"),
                    html.Hr(),
                ], width=12)
            ]),
            
            # Status Cards Row
            dbc.Row([
                # Left column
                dbc.Col([
                    # Key indicators
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.I(className="fab fa-slack me-2"),
                                "Solana Network Status"
                            ], className="d-flex align-items-center")
                        ]),
                        dbc.CardBody([
                            html.Div([
                                html.Div([
                                    html.I(className="fas fa-check-circle text-success me-2"),
                                    "Network Online"
                                ], className="d-flex align-items-center mb-3"),
                                html.Hr(className="my-3"),
                                html.Div([
                                    html.H3(id="solana-tps", children=[
                                        html.I(className="fas fa-tachometer-alt me-2"),
                                        f"{solana_network_data['tps']} TPS"
                                    ], className="mb-3"),
                                    html.H3(id="solana-slot", children=[
                                        html.I(className="fas fa-cube me-2"),
                                        f"Current Slot: {solana_network_data['current_slot']:,}"
                                    ])
                                ])
                            ])
                        ])
                    ], className="mb-4 animate-on-scroll"),
                    
                    # Market Cap Distribution
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.I(className="fas fa-chart-pie me-2"),
                                "Market Cap Distribution"
                            ], className="d-flex align-items-center")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                id="market-cap-graph",
                                figure=fig_market_cap,
                                responsive=True,
                                className="dash-graph"
                            )
                        ])
                    ], className="animate-on-scroll")
                ], width=12, lg=4),
                
                # Right column (wider)
                dbc.Col([
                    # Market Overview Card
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.I(className="fas fa-chart-bar me-2"),
                                "Market Overview"
                            ], className="d-flex align-items-center justify-content-between"),
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                id="market-overview-graph",
                                figure=fig_price,
                                responsive=True,
                                className="dash-graph mb-4"
                            ),
                            
                            html.Div([
                                html.H5("Top Performing Assets", className="mb-3"),
                                html.Div(id="market-data-container", children=[
                                    dbc.Row([
                                        dbc.Col([
                                            html.Div("Asset", className="fw-bold")
                                        ], width=2),
                                        dbc.Col([
                                            html.Div("Price", className="fw-bold")
                                        ], width=3),
                                        dbc.Col([
                                            html.Div("24h Change", className="fw-bold")
                                        ], width=3),
                                        dbc.Col([
                                            html.Div("Volume", className="fw-bold")
                                        ], width=2),
                                        dbc.Col([
                                            html.Div("Market Cap", className="fw-bold")
                                        ], width=2),
                                    ], className="mb-2"),
                                    
                                    *[
                                        dbc.Row([
                                            dbc.Col([
                                                html.Div([
                                                    asset['symbol']
                                                ])
                                            ], width=2),
                                            dbc.Col([
                                                html.Div(f"${asset['price']:,.2f}")
                                            ], width=3),
                                            dbc.Col([
                                                html.Div(
                                                    f"{asset['change']:+.2f}%", 
                                                    style={"color": "#5DFDCB" if asset['change'] >= 0 else "#FF5C5C"}
                                                )
                                            ], width=3),
                                            dbc.Col([
                                                html.Div(f"${asset['volume']}B")
                                            ], width=2),
                                            dbc.Col([
                                                html.Div(f"${asset['marketCap']}T")
                                            ], width=2),
                                        ], className="mb-3")
                                        for asset in assets
                                    ]
                                ])
                            ])
                        ])
                    ], className="mb-4 animate-on-scroll"),
                    
                    # Latest Market Analysis Card
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.I(className="fas fa-brain me-2"),
                                "Latest Market Analysis",
                                dbc.Badge("AI Generated", color="success", className="ms-2"),
                            ], className="d-flex align-items-center"),
                        ]),
                        dbc.CardBody([
                            html.P(sections[0]["content"][0] if sections and sections[0]["content"] else "", className="mb-3"),
                            dbc.Button([
                                html.I(className="fas fa-file-alt me-2"),
                                "View Full Report"
                            ], color="primary", href="/dashboard/market-analysis"),
                        ])
                    ], className="animate-on-scroll")
                ], width=12, lg=8),
            ]),
            
            # Price History and Comparison Charts Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.I(className="fas fa-chart-line me-2"),
                                "Price History (BTC & ETH)"
                            ], className="d-flex align-items-center")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                id="price-history-graph",
                                figure=fig_price_history,
                                responsive=True,
                                className="dash-graph"
                            )
                        ])
                    ], className="mb-4 animate-on-scroll")
                ], width=12, lg=6),
                
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.I(className="fas fa-chart-bar me-2"),
                                "Price Change Comparison"
                            ], className="d-flex align-items-center")
                        ]),
                        dbc.CardBody([
                            dcc.Graph(
                                id="change-comparison-graph",
                                figure=fig_change_comparison,
                                responsive=True,
                                className="dash-graph"
                            )
                        ])
                    ], className="mb-4 animate-on-scroll")
                ], width=12, lg=6)
            ]),
            
            # Enhanced Solana Metrics Row
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader([
                            html.Div([
                                html.I(className="fab fa-slack me-2"),
                                "Solana Network Metrics"
                            ], className="d-flex align-items-center")
                        ]),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.Div([
                                        html.H4(id="solana-validators", children=[
                                            html.I(className="fas fa-server me-2"),
                                            f"{solana_network_data.get('validators', {}).get('active', 'N/A')} / {solana_network_data.get('validators', {}).get('total', 'N/A')}"
                                        ], className="text-info"),
                                        html.P("Active / Total Validators")
                                    ], className="text-center")
                                ], width=12, md=4),
                                
                                dbc.Col([
                                    html.Div([
                                        html.H4(id="solana-supply", children=[
                                            html.I(className="fas fa-coins me-2"),
                                            f"{solana_network_data.get('supply', {}).get('circulating', 'N/A'):,.2f}B SOL"
                                        ], className="text-info"),
                                        html.P("Circulating Supply")
                                    ], className="text-center")
                                ], width=12, md=4),
                                
                                dbc.Col([
                                    html.Div([
                                        html.H4(id="block-time", children=[
                                            html.I(className="fas fa-clock me-2"),
                                            f"{solana_network_data.get('block_time_diff', 'N/A')} s"
                                        ] if 'block_time_diff' in solana_network_data else [
                                            html.I(className="fas fa-clock me-2"),
                                            "N/A"
                                        ], className="text-info"),
                                        html.P("Time Since Last Block")
                                    ], className="text-center")
                                ], width=12, md=4)
                            ])
                        ])
                    ], className="mb-4 animate-on-scroll")
                ], width=12)
            ]),
            
            # Market Analysis Section
            dbc.Row([
                dbc.Col([
                    html.H2("Market Analysis", className="mb-4 animate-on-scroll"),
                    html.Div(report_components)
                ], width=12)
            ], id="market-analysis-content"),
            
            # Footer
            dbc.Row([
                dbc.Col([
                    html.Hr(),
                    html.Footer([
                        html.P([
                            "HiramAbiff Dashboard • ",
                            html.Span(datetime.datetime.now().strftime("%Y")),
                            " • ", 
                            html.A("View Documentation", href="#", className="text-decoration-none")
                        ], className="text-center text-muted")
                    ])
                ], width=12)
            ])
        ], fluid=True)
    ])
    
    # Add callback for auto-refresh of market data
    @app.callback(
        [
            dash.dependencies.Output('market-overview-graph', 'figure'),
            dash.dependencies.Output('market-cap-graph', 'figure'),
            dash.dependencies.Output('market-data-container', 'children'),
            dash.dependencies.Output('solana-tps', 'children'),
            dash.dependencies.Output('solana-slot', 'children'),
            dash.dependencies.Output('price-history-graph', 'figure'),
            dash.dependencies.Output('change-comparison-graph', 'figure'),
            dash.dependencies.Output('solana-validators', 'children'),
            dash.dependencies.Output('solana-supply', 'children'),
            dash.dependencies.Output('block-time', 'children')
        ],
        [dash.dependencies.Input('market-refresh-interval', 'n_intervals')]
    )
    def refresh_market_data(n):
        # Fetch fresh crypto data
        fresh_data = fetch_real_crypto_data()
        if fresh_data:
            assets_data = fresh_data
            print(f"Refreshed market data: {len(assets_data)} assets updated")
        else:
            # Use existing data if refresh fails
            assets_data = assets
            print("Failed to refresh market data, using existing data")
        
        # Fetch fresh Solana network data
        fresh_solana_data = fetch_solana_network_data()
        if fresh_solana_data:
            solana_data = fresh_solana_data
            print(f"Refreshed Solana network data - TPS: {solana_data['tps']}, Slot: {solana_data['current_slot']}")
        else:
            # Use existing data if refresh fails
            solana_data = solana_network_data
            print("Failed to refresh Solana network data, using existing data")
        
        # Update price chart
        df = pd.DataFrame(assets_data)
        fig_price = px.bar(
            df, 
            x="symbol", 
            y="price", 
            color="change",
            color_continuous_scale=["#FF5C5C", "#F8F9FA", "#5DFDCB"],
            title="Current Asset Prices",
            labels={"symbol": "Asset", "price": "Price (USD)", "change": "24h Change (%)"},
            template="plotly_dark"
        )
        
        # Update market cap chart
        fig_market_cap = px.pie(
            df,
            values='marketCap',
            names='symbol',
            title='Market Cap Distribution (in Trillions USD)',
            hole=0.6,
            template="plotly_dark"
        )
        
        # Create historical price chart for Bitcoin
        bitcoin_data = next((asset for asset in assets_data if asset['symbol'] == 'BTC'), None)
        ethereum_data = next((asset for asset in assets_data if asset['symbol'] == 'ETH'), None)
        
        # Create a basic historical chart as default
        fig_price_history = go.Figure()
        fig_price_history.update_layout(
            title='7-Day Price History',
            template='plotly_dark'
        )
        
        if bitcoin_data and 'sparkline' in bitcoin_data and bitcoin_data['sparkline']:
            # Create timestamps for the sparkline data (7 days worth)
            now = datetime.datetime.now()
            timestamps = [now - datetime.timedelta(days=7) + datetime.timedelta(hours=i*2) for i in range(len(bitcoin_data['sparkline']))]
            
            # Create a DataFrame for the price history
            price_history_data = []
            
            # Add Bitcoin price history
            for i, price in enumerate(bitcoin_data['sparkline']):
                price_history_data.append({
                    'timestamp': timestamps[i],
                    'price': price,
                    'asset': 'BTC'
                })
                
            # Add Ethereum price history if available
            if ethereum_data and 'sparkline' in ethereum_data and ethereum_data['sparkline']:
                for i, price in enumerate(ethereum_data['sparkline']):
                    price_history_data.append({
                        'timestamp': timestamps[i],
                        'price': price,
                        'asset': 'ETH'
                    })
            
            # Create the DataFrame
            price_history_df = pd.DataFrame(price_history_data)
            
            # Create the historical price chart
            fig_price_history = px.line(
                price_history_df,
                x='timestamp',
                y='price',
                color='asset',
                title='7-Day Price History',
                template='plotly_dark',
                color_discrete_map={'BTC': '#F7931A', 'ETH': '#627EEA'}
            )
            
            fig_price_history.update_layout(
                xaxis_title='Date',
                yaxis_title='Price (USD)',
                legend_title='Asset',
                hovermode='x unified'
            )
        
        # Update price change comparison chart
        if 'change_7d' in df.columns and 'change_30d' in df.columns:
            fig_change_comparison = px.bar(
                df.sort_values('change', ascending=False),
                x='symbol',
                y=['change', 'change_7d', 'change_30d'],
                title='Price Change Comparison',
                template='plotly_dark',
                barmode='group',
                labels={
                    'symbol': 'Asset',
                    'value': 'Change (%)',
                    'variable': 'Timeframe'
                }
            )
            fig_change_comparison.update_layout(
                legend_title='Timeframe',
                yaxis_title='Change (%)'
            )
            # Rename the legend items
            newnames = {'change': '24h', 'change_7d': '7d', 'change_30d': '30d'}
            fig_change_comparison.for_each_trace(lambda t: t.update(name=newnames[t.name]))
        else:
            fig_change_comparison = px.bar(
                df.sort_values('change', ascending=False),
                x='symbol',
                y='change',
                title='24h Price Change Comparison',
                template='plotly_dark'
            )
            fig_change_comparison.update_layout(
                yaxis_title='24h Change (%)'
            )
        
        # Update asset table
        asset_rows = [
            dbc.Row([
                dbc.Col([
                    html.Div("Asset", className="fw-bold")
                ], width=2),
                dbc.Col([
                    html.Div("Price", className="fw-bold")
                ], width=3),
                dbc.Col([
                    html.Div("24h Change", className="fw-bold")
                ], width=3),
                dbc.Col([
                    html.Div("Volume", className="fw-bold")
                ], width=2),
                dbc.Col([
                    html.Div("Market Cap", className="fw-bold")
                ], width=2),
            ], className="mb-2")
        ]
        
        for asset in assets_data:
            asset_rows.append(
                dbc.Row([
                    dbc.Col([
                        html.Div([
                            asset['symbol']
                        ])
                    ], width=2),
                    dbc.Col([
                        html.Div(f"${asset['price']:,.2f}")
                    ], width=3),
                    dbc.Col([
                        html.Div(
                            f"{asset['change']:+.2f}%", 
                            style={"color": "#5DFDCB" if asset['change'] >= 0 else "#FF5C5C"}
                        )
                    ], width=3),
                    dbc.Col([
                        html.Div(f"${asset['volume']}B")
                    ], width=2),
                    dbc.Col([
                        html.Div(f"${asset['marketCap']}T")
                    ], width=2),
                ], className="mb-3")
            )
        
        # Update Solana network data
        solana_tps = [
            html.I(className="fas fa-tachometer-alt me-2"),
            f"{solana_data['tps']} TPS"
        ]
        
        solana_slot = [
            html.I(className="fas fa-cube me-2"),
            f"Current Slot: {solana_data['current_slot']:,}"
        ]
        
        # Update Solana validator data
        solana_validators = [
            html.I(className="fas fa-server me-2"),
            f"{solana_data.get('validators', {}).get('active', 'N/A')} / {solana_data.get('validators', {}).get('total', 'N/A')}"
        ]
        
        # Update Solana supply data
        solana_supply = [
            html.I(className="fas fa-coins me-2"),
            f"{solana_data.get('supply', {}).get('circulating', 'N/A'):,.2f}B SOL"
        ]
        
        # Update block time data
        block_time = [
            html.I(className="fas fa-clock me-2"),
            f"{solana_data.get('block_time_diff', 'N/A')} s"
        ] if 'block_time_diff' in solana_data else [
            html.I(className="fas fa-clock me-2"),
            "N/A"
        ]
        
        return fig_price, fig_market_cap, asset_rows, solana_tps, solana_slot, fig_price_history, fig_change_comparison, solana_validators, solana_supply, block_time
    
    # Callback to refresh market analysis
    @app.callback(
        [
            dash.dependencies.Output('market-analysis-report', 'data', allow_duplicate=True),
            dash.dependencies.Output('market-analysis-sections', 'data', allow_duplicate=True)
        ],
        [dash.dependencies.Input('analysis-refresh-interval', 'n_intervals')],
        prevent_initial_call=True
    )
    def refresh_market_analysis(n):
        print("Refreshing market analysis report...")
        fresh_report = generate_market_analysis(assets)
        
        # Parse the report content for better formatting
        sections = []
        current_section = {"title": "Summary", "content": []}
        
        for line in fresh_report["content"].split('\n'):
            if line.strip() == '':
                continue
            elif line.startswith('# '):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": line[2:], "content": []}
            elif line.startswith('## '):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": line[3:], "content": []}
            else:
                current_section["content"].append(line)
        
        if current_section["content"]:
            sections.append(current_section)
            
        print(f"Successfully refreshed market analysis with {len(sections)} sections")
        return fresh_report, sections
    
    return app

# FastAPI Application
app = FastAPI(
    title="HiramAbiff Dashboard",
    description="HiramAbiff Dashboard Demo",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root redirect
@app.get("/")
async def root():
    """Redirect to dashboard."""
    return RedirectResponse(url="/dashboard/")

# Create and mount Dashboard
dash_app = create_dashboard()
app.mount("/dashboard", dash_app.server)

# Mount static files
current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, "static")
print(f"Mounting static files from: {static_dir}")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Run application
if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='HiramAbiff Dashboard')
    parser.add_argument('--port', type=int, default=DASHBOARD_PORT,
                        help=f'Port to run the dashboard on (default: {DASHBOARD_PORT})')
    parser.add_argument('--host', type=str, default="0.0.0.0",
                        help='Host to run the dashboard on (default: 0.0.0.0)')
    args = parser.parse_args()
    
    port = args.port
    host = args.host
    
    print(f"Starting HiramAbiff Dashboard on http://{host}:{port}/dashboard/")
    dash_app.run(host=host, port=port, debug=True) 