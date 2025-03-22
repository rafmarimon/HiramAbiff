# HiramAbiff Token Data Visualization

This document provides an overview of the token data visualization capabilities within the HiramAbiff toolkit.

## Overview

The visualization module provides powerful charting and graphical analysis tools for cryptocurrency data, including:

- **Price Charts**: Visualize token price movements with volume and moving averages
- **Portfolio Distribution**: Generate pie charts showing token allocations in a portfolio
- **Token Comparisons**: Compare multiple tokens' price performance
- **Volatility Analysis**: Analyze and compare token volatility across multiple assets
- **Correlation Heatmaps**: Visualize relationships between token price movements

## Prerequisites

- Python 3.8+
- Required packages: matplotlib, seaborn, pandas, numpy (installed automatically with HiramAbiff)
- For interactive chart display: A GUI environment or Jupyter notebook

## Command Line Usage

### Single Token Price Charts

Generate a price chart for a specific token:

```bash
hiramabiff token analyze BTC --chart
```

Options:
- `--days N`: Show the last N days of data (default: 30)
- `--show`: Display the chart in a window (requires GUI environment)

### Portfolio Visualization

Generate a pie chart showing the distribution of tokens in a portfolio:

```bash
hiramabiff token portfolio ethereum:0x123... solana:abc... --chart
```

Options:
- `--show`: Display the chart in a window (requires GUI environment)

### Token Comparison

Compare multiple tokens on the same chart:

```bash
hiramabiff token compare BTC ETH SOL --days 90
```

Options:
- `--normalized`: Show percentage changes instead of absolute prices
- `--correlation`: Also generate a correlation heatmap
- `--days N`: Show the last N days of data (default: 30)
- `--show`: Display the chart in a window (requires GUI environment)

### Volatility Comparison

Compare the volatility of multiple tokens:

```bash
hiramabiff token volatility BTC ETH SOL DOGE
```

Options:
- `--show`: Display the chart in a window (requires GUI environment)

## Programmatic Usage

You can also use the visualization tools directly in your Python code:

```python
from hiramabiff.analysis import TokenTracker, TokenVisualizer
import pandas as pd
import asyncio

async def generate_charts():
    # Initialize components
    token_tracker = TokenTracker()
    visualizer = TokenVisualizer()
    
    # Get token data
    historical_data = await token_tracker.get_token_historical_data("BTC", days=30)
    df = pd.DataFrame(historical_data["price_data"])
    
    # Create a price chart
    chart_path = visualizer.create_price_chart(
        df, 
        "BTC", 
        days=30,
        show_volume=True,
        show_ma=True,
        ma_periods=[7, 30],
        save=True,
        show=False  # Set to True to display
    )
    print(f"Chart saved to: {chart_path}")
    
    # Create a portfolio chart (with example data)
    portfolio_data = {
        "total_value_usd": 10000,
        "token_distribution": {
            "BTC": {"percentage": 40, "value_usd": 4000},
            "ETH": {"percentage": 30, "value_usd": 3000},
            "SOL": {"percentage": 20, "value_usd": 2000},
            "DOGE": {"percentage": 10, "value_usd": 1000}
        }
    }
    
    pie_chart_path = visualizer.create_portfolio_pie_chart(
        portfolio_data,
        title="My Portfolio",
        min_pct=2.0,
        save=True,
        show=False
    )
    print(f"Portfolio chart saved to: {pie_chart_path}")

# Run the async function
asyncio.run(generate_charts())
```

## Customizing Charts

The `TokenVisualizer` class provides several customization options:

### Color Schemes

All chart methods accept a `color_scheme` parameter, with the following options:

- `"primary"`: Default colors
- `"pastel"`: Soft pastel colors
- `"dark"`: Dark colors
- `"colorblind"`: Colorblind-friendly palette
- `"deep"`: Deep, rich colors

### Output Directory

By default, charts are saved to `~/.hiramabiff/visualizations/` in subdirectories based on chart type. You can specify a custom directory when initializing the visualizer:

```python
visualizer = TokenVisualizer(output_dir="/path/to/my/charts")
```

## Chart Types and Features

### Price Charts

Price charts include:
- Price line
- Volume bars (if data available)
- Moving averages (7-day and 30-day by default)
- Min/max price indicators
- Formatted money values on y-axis

### Portfolio Pie Charts

Portfolio pie charts include:
- Token distribution by percentage
- Grouped small allocations as "Other"
- Total portfolio value annotation

### Comparison Charts

Comparison charts include:
- Multiple token price lines
- Optional normalization to percentage change
- Formatted dates on x-axis

### Volatility Charts

Volatility comparison charts include:
- Scatter plot of volatility vs price
- Bubble size representing market cap
- Token labels

### Correlation Heatmaps

Correlation heatmaps include:
- Matrix of correlation coefficients
- Color-coded correlation strength
- Annotation with correlation values

## Troubleshooting

### Common Issues

1. **Chart display not working**: Make sure you have a GUI environment available if using the `--show` option.

2. **Missing data**: If a chart looks incomplete, try reducing the time range using `--days` or check if the token has the data available.

3. **'Agg' backend warning**: This is normal when displaying in environments without GUI support. Use the saved file path to view the chart.

### Debug Visualization Issues

For debugging visualization issues, you can enable verbose logging:

```bash
hiramabiff --verbose token analyze BTC --chart
```

## Integration with Analysis

Visualizations work seamlessly with token analysis and LLM features. For example:

```bash
# Analyze a token, generate a chart, and get LLM insights
hiramabiff token analyze ETH --chart --llm

# Analyze a portfolio, generate a pie chart, and get LLM insights
hiramabiff token portfolio ethereum:0x123... --chart --llm
``` 