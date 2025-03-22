#!/usr/bin/env python
"""
Token Visualization Demo

This script demonstrates the visualization capabilities of HiramAbiff
by creating various charts for token analysis and portfolio visualization.
"""

import asyncio
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

# Add the parent directory to the path if running directly
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the required modules from HiramAbiff
try:
    # Try normal import if installed as a package
    from hiramabiff.analysis import TokenTracker, TokenVisualizer
except ImportError:
    # For direct runs without package installation
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
    try:
        from hiramabiff.analysis import TokenTracker, TokenVisualizer
    except ImportError:
        # Last resort, try direct module imports
        from src.hiramabiff.analysis.token_tracker import TokenTracker
        from src.hiramabiff.analysis.visualizer import TokenVisualizer

# Set up logging directory
import logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("visualization_demo")

# We'll modify the demo to use a simpler approach for testing
async def demo_price_chart():
    """Demonstrate creating a token price chart."""
    print("\n1. Creating token price chart...")
    token_tracker = TokenTracker()
    visualizer = TokenVisualizer()
    
    # For testing purposes, we'll simulate data instead of fetching it
    # This removes dependencies on external APIs during testing
    print(f"Generating sample price data...")
    
    # Create sample data spanning 30 days
    dates = [datetime.now() - timedelta(days=i) for i in range(30)]
    dates.reverse()  # Make dates go from oldest to newest
    
    # Generate simulated price data with some randomness and trend
    base_price = 30000  # Starting price
    prices = [base_price]
    for i in range(1, 30):
        # Add some randomness to the price movement
        change = np.random.normal(0, 500)  # Random change with normal distribution
        # Add a slight upward trend
        trend = 100 if i > 15 else -50  # Downtrend then uptrend
        new_price = max(100, prices[-1] + change + trend)  # Ensure price doesn't go below 100
        prices.append(new_price)
    
    # Generate random volumes
    volumes = [np.random.randint(1000000, 5000000) for _ in range(30)]
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'price': prices,
        'volume': volumes
    })
    
    # Create price chart
    print("Creating price chart with moving averages and volume...")
    chart_path = visualizer.create_price_chart(
        df,
        "BTC",
        days=30,
        show_volume=True,
        show_ma=True,
        ma_periods=[7, 14, 30],
        save=True,
        show=False  # Set to True to display in a window
    )
    
    print(f"Chart saved to: {chart_path}")
    return chart_path


async def demo_portfolio_chart():
    """Demonstrate creating a portfolio distribution chart."""
    print("\n2. Creating portfolio distribution chart...")
    visualizer = TokenVisualizer()
    
    # Create sample portfolio data
    portfolio_data = {
        "total_value_usd": 10000,
        "token_distribution": {
            "BTC": {"percentage": 35, "value_usd": 3500},
            "ETH": {"percentage": 25, "value_usd": 2500},
            "SOL": {"percentage": 15, "value_usd": 1500},
            "AVAX": {"percentage": 10, "value_usd": 1000},
            "MATIC": {"percentage": 5, "value_usd": 500},
            "LINK": {"percentage": 4, "value_usd": 400},
            "DOT": {"percentage": 3, "value_usd": 300},
            "ADA": {"percentage": 2, "value_usd": 200},
            "XLM": {"percentage": 1, "value_usd": 100},
        }
    }
    
    # Create portfolio pie chart
    print("Creating portfolio distribution pie chart...")
    chart_path = visualizer.create_portfolio_pie_chart(
        portfolio_data,
        title="Demo Portfolio Distribution",
        min_pct=3.0,  # Group tokens less than 3% into "Other"
        save=True,
        show=False  # Set to True to display in a window
    )
    
    print(f"Chart saved to: {chart_path}")
    return chart_path


async def demo_compare_tokens():
    """Demonstrate creating a token comparison chart."""
    print("\n3. Creating token comparison chart...")
    visualizer = TokenVisualizer()
    
    # For testing, generate simulated data for multiple tokens
    tokens = ["BTC", "ETH", "SOL"]
    data_frames = {}
    
    # Create 90 days of data
    dates = [datetime.now() - timedelta(days=i) for i in range(90)]
    dates.reverse()  # Make dates go from oldest to newest
    
    for symbol in tokens:
        print(f"Generating sample data for {symbol}...")
        
        # Generate different price ranges for each token
        if symbol == "BTC":
            base_price = 30000
            volatility = 500
        elif symbol == "ETH":
            base_price = 2000
            volatility = 100
        else:  # SOL
            base_price = 100
            volatility = 5
        
        # Generate simulated price data with correlations
        prices = [base_price]
        for i in range(1, 90):
            # Add some randomness to the price movement
            change = np.random.normal(0, volatility)
            
            # Add a market trend component (shared across tokens)
            market_trend = 0.2 * np.sin(i/15) * base_price * 0.05
            
            # Add token-specific trend
            if symbol == "BTC":
                token_trend = np.sin(i/30) * base_price * 0.02
            elif symbol == "ETH":
                token_trend = np.sin(i/25) * base_price * 0.03
            else:  # SOL
                token_trend = np.sin(i/20) * base_price * 0.04
                
            new_price = max(prices[-1] + change + market_trend + token_trend, base_price * 0.7)
            prices.append(new_price)
        
        # Generate random volumes
        volumes = [np.random.randint(int(base_price * 100), int(base_price * 500)) for _ in range(90)]
        
        # Create DataFrame
        df = pd.DataFrame({
            'timestamp': dates,
            'price': prices,
            'volume': volumes
        })
        
        data_frames[symbol] = df
    
    # Create normalized comparison chart
    print("Creating normalized comparison chart...")
    norm_path = visualizer.create_multi_token_chart(
        data_frames,
        days=90,
        normalized=True,
        save=True,
        show=False  # Set to True to display in a window
    )
    
    print(f"Normalized comparison chart saved to: {norm_path}")
    
    # Create correlation heatmap
    print("Creating correlation heatmap...")
    corr_path = visualizer.create_price_correlation_heatmap(
        data_frames,
        days=90,
        save=True,
        show=False  # Set to True to display in a window
    )
    
    print(f"Correlation heatmap saved to: {corr_path}")
    return norm_path, corr_path


async def demo_volatility_comparison():
    """Demonstrate creating a volatility comparison chart."""
    print("\n4. Creating volatility comparison chart...")
    visualizer = TokenVisualizer()
    
    # Generate sample token analyses
    tokens = ["BTC", "ETH", "SOL", "DOGE", "XRP"]
    token_analyses = {}
    
    for i, symbol in enumerate(tokens):
        print(f"Generating analysis data for {symbol}...")
        
        # Create sample analysis with different characteristics for each token
        if symbol == "BTC":
            price = 40000
            market_cap = 800000000000
            volatility = 0.03
        elif symbol == "ETH":
            price = 2500
            market_cap = 300000000000
            volatility = 0.04
        elif symbol == "SOL":
            price = 120
            market_cap = 50000000000
            volatility = 0.06
        elif symbol == "DOGE":
            price = 0.08
            market_cap = 12000000000
            volatility = 0.09
        else:  # XRP
            price = 0.5
            market_cap = 25000000000
            volatility = 0.05
        
        token_analyses[symbol] = {
            "symbol": symbol,
            "current_price_usd": price,
            "market_cap_usd": market_cap,
            "stats": {"volatility_30d": volatility}
        }
    
    # Create volatility comparison chart
    print("Creating volatility vs. price chart...")
    chart_path = visualizer.create_volatility_comparison(
        token_analyses,
        save=True,
        show=False  # Set to True to display in a window
    )
    
    print(f"Volatility comparison chart saved to: {chart_path}")
    return chart_path


async def run_all_demos():
    """Run all demo functions."""
    # Create results directory
    results_dir = os.path.join(os.path.dirname(__file__), "visualization_results")
    os.makedirs(results_dir, exist_ok=True)
    
    print("=" * 50)
    print("HiramAbiff Token Visualization Demo")
    print("=" * 50)
    
    try:
        # Demo: Price Chart
        price_chart = await demo_price_chart()
        
        # Demo: Portfolio Chart
        portfolio_chart = await demo_portfolio_chart()
        
        # Demo: Compare Tokens
        norm_chart, corr_chart = await demo_compare_tokens()
        
        # Demo: Volatility Comparison
        vol_chart = await demo_volatility_comparison()
        
        print("\n" + "=" * 50)
        print("Demo Complete")
        print("=" * 50)
        print("\nGenerated Charts:")
        print(f"1. Price Chart: {price_chart}")
        print(f"2. Portfolio Chart: {portfolio_chart}")
        print(f"3. Normalized Comparison Chart: {norm_chart}")
        print(f"4. Correlation Heatmap: {corr_chart}")
        print(f"5. Volatility Comparison: {vol_chart}")
        
        print("\nTo view the charts, check the file paths above.")
        print("The charts have been saved to the specified locations.")
    except Exception as e:
        print(f"\nError during demo: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(run_all_demos())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")
    except Exception as e:
        print(f"\nError during demo: {e}")
        import traceback
        traceback.print_exc() 