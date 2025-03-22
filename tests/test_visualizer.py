#!/usr/bin/env python
"""
Test module for the TokenVisualizer class
"""

import os
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import the TokenVisualizer class
try:
    from hiramabiff.analysis import TokenVisualizer
except ImportError:
    import sys
    import os
    
    # Add the parent directory to the path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from src.hiramabiff.analysis import TokenVisualizer


# Create a temporary directory for test outputs
@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "test_visualizations"
    output_dir.mkdir()
    return str(output_dir)


# Create sample data for testing
@pytest.fixture
def sample_price_data():
    """Create sample price data for testing."""
    # Create 30 days of data
    dates = [datetime.now() - timedelta(days=i) for i in range(30)]
    
    # Generate random prices with a trend
    base_price = 50000
    prices = [base_price]
    for i in range(1, 30):
        change = np.random.normal(0, 500)  # Random change with normal distribution
        prices.append(max(100, prices[-1] + change))  # Ensure price doesn't go below 100
    
    # Generate random volumes
    volumes = [np.random.randint(1000000, 5000000) for _ in range(30)]
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': dates,
        'price': prices,
        'volume': volumes
    })
    
    return df


@pytest.fixture
def sample_portfolio_data():
    """Create sample portfolio data for testing."""
    return {
        "total_value_usd": 10000,
        "token_distribution": {
            "BTC": {"percentage": 40, "value_usd": 4000},
            "ETH": {"percentage": 30, "value_usd": 3000},
            "SOL": {"percentage": 20, "value_usd": 2000},
            "DOGE": {"percentage": 5, "value_usd": 500},
            "ADA": {"percentage": 3, "value_usd": 300},
            "DOT": {"percentage": 2, "value_usd": 200}
        }
    }


# Test initialization
def test_visualizer_init(temp_output_dir):
    """Test that the visualizer initializes correctly."""
    visualizer = TokenVisualizer(output_dir=temp_output_dir)
    
    # Check that output directories were created
    assert os.path.exists(temp_output_dir)
    assert os.path.exists(os.path.join(temp_output_dir, "price_charts"))
    assert os.path.exists(os.path.join(temp_output_dir, "portfolio"))
    assert os.path.exists(os.path.join(temp_output_dir, "comparisons"))
    
    # Check that color schemes were configured
    assert "primary" in visualizer.color_schemes
    assert "pastel" in visualizer.color_schemes
    assert "dark" in visualizer.color_schemes
    assert "colorblind" in visualizer.color_schemes
    assert "deep" in visualizer.color_schemes


# Test price chart creation
def test_create_price_chart(temp_output_dir, sample_price_data):
    """Test creating a price chart."""
    visualizer = TokenVisualizer(output_dir=temp_output_dir)
    
    # Create chart
    output_path = visualizer.create_price_chart(
        sample_price_data,
        symbol="BTC",
        days=30,
        show_volume=True,
        show_ma=True,
        ma_periods=[7, 14],
        save=True,
        show=False
    )
    
    # Check that file was created
    assert os.path.exists(output_path)
    assert output_path.endswith(".png")
    assert os.path.getsize(output_path) > 0  # File should not be empty


# Test portfolio pie chart creation
def test_create_portfolio_pie_chart(temp_output_dir, sample_portfolio_data):
    """Test creating a portfolio pie chart."""
    visualizer = TokenVisualizer(output_dir=temp_output_dir)
    
    # Create chart
    output_path = visualizer.create_portfolio_pie_chart(
        sample_portfolio_data,
        title="Test Portfolio",
        min_pct=2.0,
        save=True,
        show=False
    )
    
    # Check that file was created
    assert os.path.exists(output_path)
    assert output_path.endswith(".png")
    assert os.path.getsize(output_path) > 0  # File should not be empty


# Test multi-token chart creation
def test_create_multi_token_chart(temp_output_dir, sample_price_data):
    """Test creating a multi-token chart."""
    visualizer = TokenVisualizer(output_dir=temp_output_dir)
    
    # Create multiple token DataFrames with slight variations
    btc_data = sample_price_data.copy()
    eth_data = sample_price_data.copy()
    eth_data['price'] = eth_data['price'] * 0.06  # ETH at ~6% of BTC price
    
    # Add some random variation to make them different
    for i in range(len(eth_data)):
        eth_data.loc[i, 'price'] = eth_data.loc[i, 'price'] * (1 + np.random.normal(0, 0.02))
    
    data_frames = {
        "BTC": btc_data,
        "ETH": eth_data
    }
    
    # Test normalized chart
    norm_path = visualizer.create_multi_token_chart(
        data_frames,
        days=30,
        normalized=True,
        save=True,
        show=False
    )
    
    # Check that files were created
    assert os.path.exists(norm_path)
    assert norm_path.endswith(".png")
    assert os.path.getsize(norm_path) > 0
    
    # Test absolute price chart
    abs_path = visualizer.create_multi_token_chart(
        data_frames,
        days=30,
        normalized=False,
        save=True,
        show=False
    )
    
    assert os.path.exists(abs_path)
    assert abs_path.endswith(".png")
    assert os.path.getsize(abs_path) > 0


# Test correlation heatmap creation
def test_create_correlation_heatmap(temp_output_dir, sample_price_data):
    """Test creating a correlation heatmap."""
    visualizer = TokenVisualizer(output_dir=temp_output_dir)
    
    # Create multiple token DataFrames with different correlations
    btc_data = sample_price_data.copy()
    eth_data = sample_price_data.copy()
    sol_data = sample_price_data.copy()
    
    # Make ETH highly correlated with BTC
    eth_data['price'] = btc_data['price'] * 0.06 + np.random.normal(0, 100, len(btc_data))
    
    # Make SOL less correlated
    for i in range(len(sol_data)):
        if i > 0:
            # Add some independent movement
            change = np.random.normal(0, 300)
            sol_data.loc[i, 'price'] = max(100, sol_data.loc[i-1, 'price'] + change)
    
    data_frames = {
        "BTC": btc_data,
        "ETH": eth_data,
        "SOL": sol_data
    }
    
    # Create heatmap
    output_path = visualizer.create_price_correlation_heatmap(
        data_frames,
        days=30,
        save=True,
        show=False
    )
    
    # Check that file was created
    assert os.path.exists(output_path)
    assert output_path.endswith(".png")
    assert os.path.getsize(output_path) > 0


# Test volatility comparison chart
def test_create_volatility_comparison(temp_output_dir):
    """Test creating a volatility comparison chart."""
    visualizer = TokenVisualizer(output_dir=temp_output_dir)
    
    # Create token analyses
    token_analyses = {
        "BTC": {
            "symbol": "BTC",
            "current_price_usd": 50000,
            "market_cap_usd": 1000000000000,
            "stats": {"volatility_30d": 0.03}
        },
        "ETH": {
            "symbol": "ETH",
            "current_price_usd": 3000,
            "market_cap_usd": 400000000000,
            "stats": {"volatility_30d": 0.04}
        },
        "SOL": {
            "symbol": "SOL",
            "current_price_usd": 100,
            "market_cap_usd": 40000000000,
            "stats": {"volatility_30d": 0.06}
        },
        "DOGE": {
            "symbol": "DOGE",
            "current_price_usd": 0.1,
            "market_cap_usd": 10000000000,
            "stats": {"volatility_30d": 0.08}
        }
    }
    
    # Create chart
    output_path = visualizer.create_volatility_comparison(
        token_analyses,
        save=True,
        show=False
    )
    
    # Check that file was created
    assert os.path.exists(output_path)
    assert output_path.endswith(".png")
    assert os.path.getsize(output_path) > 0


if __name__ == "__main__":
    pytest.main(["-v", __file__]) 