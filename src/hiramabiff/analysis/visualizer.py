#!/usr/bin/env python
"""
Token Data Visualization Module

This module provides functionality for generating visualizations from token data,
including price charts, portfolio distribution, and other analytics.
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import seaborn as sns
from loguru import logger

# Set Seaborn style
sns.set_style("darkgrid")
plt.rcParams["figure.figsize"] = (12, 7)
plt.rcParams["font.size"] = 12


class TokenVisualizer:
    """A class for generating visualizations from token data."""
    
    def __init__(self, output_dir: str = None):
        """Initialize the token visualizer.
        
        Args:
            output_dir: Directory for saving visualizations
        """
        # Set up output directory
        if output_dir is None:
            home_dir = os.path.expanduser("~")
            self.output_dir = os.path.join(home_dir, ".hiramabiff", "visualizations")
        else:
            self.output_dir = output_dir
            
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create subdirectories
        self.price_charts_dir = os.path.join(self.output_dir, "price_charts")
        self.portfolio_charts_dir = os.path.join(self.output_dir, "portfolio")
        self.comparison_charts_dir = os.path.join(self.output_dir, "comparisons")
        
        os.makedirs(self.price_charts_dir, exist_ok=True)
        os.makedirs(self.portfolio_charts_dir, exist_ok=True)
        os.makedirs(self.comparison_charts_dir, exist_ok=True)
        
        # Configure color schemes
        self.color_schemes = {
            "primary": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", 
                        "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"],
            "pastel": sns.color_palette("pastel"),
            "dark": sns.color_palette("dark"),
            "colorblind": sns.color_palette("colorblind"),
            "deep": sns.color_palette("deep"),
        }
        
    def _money_formatter(self, x: float, pos) -> str:
        """Format y-axis ticks as money values.
        
        Args:
            x: Value to format
            pos: Position
            
        Returns:
            Formatted string
        """
        if x >= 1e9:
            return f"${x/1e9:.1f}B"
        elif x >= 1e6:
            return f"${x/1e6:.1f}M"
        elif x >= 1e3:
            return f"${x/1e3:.1f}K"
        else:
            return f"${x:.2f}"
    
    def create_price_chart(
        self, 
        historical_data: pd.DataFrame, 
        symbol: str,
        days: int = 30,
        show_volume: bool = True,
        show_ma: bool = True,
        ma_periods: List[int] = [7, 30],
        color_scheme: str = "primary",
        save: bool = True,
        show: bool = False,
    ) -> str:
        """Create a price chart for a token.
        
        Args:
            historical_data: DataFrame with historical price data
            symbol: Token symbol
            days: Number of days to display
            show_volume: Whether to show volume
            show_ma: Whether to show moving averages
            ma_periods: List of periods for moving averages
            color_scheme: Color scheme name
            save: Whether to save the chart
            show: Whether to display the chart
            
        Returns:
            Path to saved chart if save=True, else empty string
        """
        logger.info(f"Creating price chart for {symbol} ({days} days)")
        
        # Ensure data is sorted by timestamp
        df = historical_data.sort_values("timestamp").copy()
        
        # Filter for the requested number of days
        if len(df) > days:
            df = df.tail(days)
        
        # Create figure with secondary y-axis for volume
        fig, ax1 = plt.subplots()
        
        if show_volume:
            # Twin the x-axis for volume
            ax2 = ax1.twinx()
        
        # Plot price line
        colors = self.color_schemes.get(color_scheme, self.color_schemes["primary"])
        ax1.plot(df["timestamp"], df["price"], color=colors[0], linewidth=2, label=f"{symbol} Price")
        
        # Add moving averages if requested
        if show_ma:
            for i, period in enumerate(ma_periods):
                if len(df) >= period:
                    df[f"MA{period}"] = df["price"].rolling(window=period).mean()
                    ax1.plot(
                        df["timestamp"], 
                        df[f"MA{period}"],
                        color=colors[i+1],
                        linewidth=1.5,
                        alpha=0.7,
                        label=f"{period}-day MA"
                    )
        
        # Plot volume if requested
        if show_volume and "volume" in df.columns:
            ax2.bar(
                df["timestamp"],
                df["volume"],
                alpha=0.3,
                color=colors[-1],
                width=0.8,
                label="Volume"
            )
            ax2.set_ylabel("Volume (USD)")
            ax2.tick_params(axis="y")
            ax2.legend(loc="upper right")
            
            # Format y-axis as money
            ax2.yaxis.set_major_formatter(FuncFormatter(self._money_formatter))
        
        # Configure axes
        ax1.set_xlabel("Date")
        ax1.set_ylabel(f"Price (USD)")
        ax1.tick_params(axis="y")
        
        # Format x-axis dates
        if days <= 14:
            ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
            plt.xticks(rotation=45)
        else:
            ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
            plt.xticks(rotation=45)
        
        # Format y-axis as money
        ax1.yaxis.set_major_formatter(FuncFormatter(self._money_formatter))
        
        # Add legend, title, and grid
        ax1.legend(loc="upper left")
        plt.title(f"{symbol} Price Chart - {days} Days", fontsize=16)
        plt.grid(True, alpha=0.3)
        
        # Add min and max points
        min_price = df["price"].min()
        max_price = df["price"].max()
        min_idx = df["price"].idxmin()
        max_idx = df["price"].idxmax()
        
        ax1.scatter(df.loc[min_idx, "timestamp"], min_price, color="red", s=100, zorder=5)
        ax1.scatter(df.loc[max_idx, "timestamp"], max_price, color="green", s=100, zorder=5)
        
        ax1.annotate(
            f"${min_price:.2f}", 
            (df.loc[min_idx, "timestamp"], min_price),
            xytext=(0, -20),
            textcoords="offset points",
            ha="center"
        )
        
        ax1.annotate(
            f"${max_price:.2f}", 
            (df.loc[max_idx, "timestamp"], max_price),
            xytext=(0, 20),
            textcoords="offset points",
            ha="center"
        )
        
        # Adjust layout and figure size
        plt.tight_layout()
        
        # Save the chart if requested
        output_path = ""
        if save:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"{symbol.lower()}_price_chart_{days}d_{timestamp}.png"
            output_path = os.path.join(self.price_charts_dir, filename)
            plt.savefig(output_path, dpi=300)
            logger.info(f"Price chart saved to {output_path}")
        
        # Show the chart if requested
        if show:
            plt.show()
        else:
            plt.close()
            
        return output_path
    
    def create_multi_token_chart(
        self,
        data_frames: Dict[str, pd.DataFrame],
        days: int = 30,
        normalized: bool = True,
        color_scheme: str = "deep",
        save: bool = True,
        show: bool = False,
    ) -> str:
        """Create a comparison chart for multiple tokens.
        
        Args:
            data_frames: Dict mapping token symbols to DataFrames with historical data
            days: Number of days to display
            normalized: Whether to normalize prices to percentage change
            color_scheme: Color scheme name
            save: Whether to save the chart
            show: Whether to display the chart
            
        Returns:
            Path to saved chart if save=True, else empty string
        """
        if not data_frames:
            logger.warning("No data provided for multi-token chart")
            return ""
            
        symbols = list(data_frames.keys())
        logger.info(f"Creating comparison chart for {', '.join(symbols)} ({days} days)")
        
        plt.figure(figsize=(12, 7))
        colors = self.color_schemes.get(color_scheme, self.color_schemes["deep"])
        
        # Plot each token
        for i, (symbol, df) in enumerate(data_frames.items()):
            # Sort and filter data
            df = df.sort_values("timestamp").copy()
            if len(df) > days:
                df = df.tail(days)
                
            # Normalize if requested
            if normalized and len(df) > 0:
                base_price = df["price"].iloc[0]
                df["normalized"] = (df["price"] / base_price - 1) * 100
                plt.plot(
                    df["timestamp"], 
                    df["normalized"], 
                    label=symbol,
                    color=colors[i % len(colors)],
                    linewidth=2
                )
            else:
                plt.plot(
                    df["timestamp"], 
                    df["price"], 
                    label=symbol,
                    color=colors[i % len(colors)],
                    linewidth=2
                )
        
        # Configure axes
        plt.xlabel("Date")
        if normalized:
            plt.ylabel("Percentage Change (%)")
            plt.axhline(y=0, color="gray", linestyle="--", alpha=0.7)
        else:
            plt.ylabel("Price (USD)")
            plt.gca().yaxis.set_major_formatter(FuncFormatter(self._money_formatter))
        
        # Format x-axis dates
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        plt.xticks(rotation=45)
        
        # Add legend, title, and grid
        plt.legend(loc="best")
        if normalized:
            plt.title(f"Price Performance Comparison - {days} Days (%)", fontsize=16)
        else:
            plt.title(f"Price Comparison - {days} Days", fontsize=16)
            
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save the chart if requested
        output_path = ""
        if save:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            symbols_str = "_".join([s.lower() for s in symbols])
            if len(symbols_str) > 50:  # Avoid overly long filenames
                symbols_str = f"{len(symbols)}_tokens"
                
            normalized_str = "normalized" if normalized else "absolute"
            filename = f"comparison_{symbols_str}_{days}d_{normalized_str}_{timestamp}.png"
            output_path = os.path.join(self.comparison_charts_dir, filename)
            plt.savefig(output_path, dpi=300)
            logger.info(f"Comparison chart saved to {output_path}")
        
        # Show the chart if requested
        if show:
            plt.show()
        else:
            plt.close()
            
        return output_path
    
    def create_portfolio_pie_chart(
        self,
        portfolio_data: Dict[str, Any],
        title: str = "Portfolio Distribution",
        min_pct: float = 2.0,
        color_scheme: str = "pastel",
        save: bool = True,
        show: bool = False,
    ) -> str:
        """Create a pie chart for portfolio distribution.
        
        Args:
            portfolio_data: Portfolio data from TokenTracker
            title: Chart title
            min_pct: Minimum percentage for individual slice (smaller grouped as 'Other')
            color_scheme: Color scheme name
            save: Whether to save the chart
            show: Whether to display the chart
            
        Returns:
            Path to saved chart if save=True, else empty string
        """
        logger.info("Creating portfolio distribution pie chart")
        
        # Extract token distribution
        token_distribution = portfolio_data.get("token_distribution", {})
        if not token_distribution:
            logger.warning("No token distribution data in portfolio")
            return ""
        
        # Get token percentages and values
        tokens = []
        percentages = []
        values = []
        for token, data in token_distribution.items():
            tokens.append(token)
            percentages.append(data.get("percentage", 0))
            values.append(data.get("value_usd", 0))
        
        # Group small percentages into 'Other'
        if min_pct > 0:
            grouped_tokens = []
            grouped_percentages = []
            grouped_values = []
            other_pct = 0
            other_value = 0
            
            for token, pct, value in zip(tokens, percentages, values):
                if pct >= min_pct:
                    grouped_tokens.append(token)
                    grouped_percentages.append(pct)
                    grouped_values.append(value)
                else:
                    other_pct += pct
                    other_value += value
            
            if other_pct > 0:
                grouped_tokens.append("Other")
                grouped_percentages.append(other_pct)
                grouped_values.append(other_value)
                
            tokens = grouped_tokens
            percentages = grouped_percentages
            values = grouped_values
        
        # Sort by percentage (descending)
        sorted_indices = np.argsort(percentages)[::-1]
        tokens = [tokens[i] for i in sorted_indices]
        percentages = [percentages[i] for i in sorted_indices]
        values = [values[i] for i in sorted_indices]
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        colors = self.color_schemes.get(color_scheme, self.color_schemes["pastel"])
        
        # Plot the pie
        wedges, texts, autotexts = plt.pie(
            percentages, 
            labels=tokens, 
            autopct="%1.1f%%",
            startangle=90,
            colors=colors,
            wedgeprops={"edgecolor": "w", "linewidth": 1},
            textprops={"fontsize": 12},
        )
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_fontsize(10)
            autotext.set_weight("bold")
        
        # Add title and make circular
        plt.title(title, fontsize=16, pad=20)
        plt.axis("equal")
        
        # Add total value annotation
        total_value = portfolio_data.get("total_value_usd", 0)
        plt.annotate(
            f"Total Value: ${total_value:,.2f}",
            xy=(0, 0),
            xytext=(0, -30),
            textcoords="offset points",
            ha="center",
            fontsize=12,
            bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.8)
        )
        
        plt.tight_layout()
        
        # Save the chart if requested
        output_path = ""
        if save:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"portfolio_distribution_{timestamp}.png"
            output_path = os.path.join(self.portfolio_charts_dir, filename)
            plt.savefig(output_path, dpi=300)
            logger.info(f"Portfolio pie chart saved to {output_path}")
        
        # Show the chart if requested
        if show:
            plt.show()
        else:
            plt.close()
            
        return output_path
    
    def create_volatility_comparison(
        self,
        token_analyses: Dict[str, Dict[str, Any]],
        color_scheme: str = "deep",
        save: bool = True,
        show: bool = False,
    ) -> str:
        """Create a volatility comparison chart for multiple tokens.
        
        Args:
            token_analyses: Dict mapping symbols to token analysis results
            color_scheme: Color scheme name
            save: Whether to save the chart
            show: Whether to display the chart
            
        Returns:
            Path to saved chart if save=True, else empty string
        """
        logger.info(f"Creating volatility comparison for {len(token_analyses)} tokens")
        
        symbols = []
        volatilities = []
        prices = []
        market_caps = []
        
        # Extract data
        for symbol, analysis in token_analyses.items():
            volatility = analysis.get("stats", {}).get("volatility_30d")
            price = analysis.get("current_price_usd")
            market_cap = analysis.get("market_cap_usd")
            
            if volatility is not None and price is not None and market_cap is not None:
                symbols.append(symbol)
                volatilities.append(volatility)
                prices.append(price)
                market_caps.append(market_cap)
        
        if not symbols:
            logger.warning("No valid data for volatility comparison")
            return ""
        
        # Create figure
        plt.figure(figsize=(14, 8))
        colors = self.color_schemes.get(color_scheme, self.color_schemes["deep"])
        
        # Normalize market caps for bubble size (between 100 and 1000)
        min_market_cap = min(market_caps)
        max_market_cap = max(market_caps)
        
        if min_market_cap == max_market_cap:
            # Avoid division by zero
            normalized_caps = [500] * len(market_caps)
        else:
            normalized_caps = [
                100 + (cap - min_market_cap) / (max_market_cap - min_market_cap) * 900
                for cap in market_caps
            ]
        
        # Create scatter plot
        scatter = plt.scatter(
            volatilities,
            prices,
            s=normalized_caps,
            c=colors[:len(symbols)],
            alpha=0.7,
            edgecolors="white",
            linewidths=1,
        )
        
        # Add token labels
        for i, symbol in enumerate(symbols):
            plt.annotate(
                symbol,
                (volatilities[i], prices[i]),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=10,
                fontweight="bold",
            )
        
        # Configure axes
        plt.xlabel("30-Day Volatility", fontsize=12)
        plt.ylabel("Current Price (USD)", fontsize=12)
        plt.title("Token Volatility vs. Price Comparison", fontsize=16)
        plt.grid(True, alpha=0.3)
        
        # Format y-axis as money
        plt.gca().yaxis.set_major_formatter(FuncFormatter(self._money_formatter))
        
        # Add legend for bubble size
        sizes = [min(normalized_caps), (min(normalized_caps) + max(normalized_caps)) / 2, max(normalized_caps)]
        labels = [
            f"${min_market_cap / 1e6:.1f}M",
            f"${(min_market_cap + max_market_cap) / 2 / 1e6:.1f}M",
            f"${max_market_cap / 1e6:.1f}M"
        ]
        
        # Create a legend for market cap sizes
        for size, label in zip(sizes, labels):
            plt.scatter([], [], s=size, c="gray", alpha=0.7, edgecolors="white", linewidths=1, label=label)
            
        plt.legend(title="Market Cap", loc="upper right", frameon=True)
        
        plt.tight_layout()
        
        # Save the chart if requested
        output_path = ""
        if save:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            tokens_str = "_".join([s.lower() for s in symbols])
            if len(tokens_str) > 50:
                tokens_str = f"{len(symbols)}_tokens"
                
            filename = f"volatility_comparison_{tokens_str}_{timestamp}.png"
            output_path = os.path.join(self.comparison_charts_dir, filename)
            plt.savefig(output_path, dpi=300)
            logger.info(f"Volatility comparison chart saved to {output_path}")
        
        # Show the chart if requested
        if show:
            plt.show()
        else:
            plt.close()
            
        return output_path
    
    def create_price_correlation_heatmap(
        self,
        data_frames: Dict[str, pd.DataFrame],
        days: int = 30,
        color_scheme: str = "coolwarm",
        save: bool = True,
        show: bool = False,
    ) -> str:
        """Create a price correlation heatmap for multiple tokens.
        
        Args:
            data_frames: Dict mapping token symbols to DataFrames with historical data
            days: Number of days to analyze
            color_scheme: Color scheme name
            save: Whether to save the chart
            show: Whether to display the chart
            
        Returns:
            Path to saved chart if save=True, else empty string
        """
        logger.info(f"Creating price correlation heatmap for {len(data_frames)} tokens")
        
        if len(data_frames) < 2:
            logger.warning("Need at least 2 tokens for correlation analysis")
            return ""
        
        # Extract and align price data
        aligned_data = {}
        
        for symbol, df in data_frames.items():
            df = df.sort_values("timestamp").copy()
            if len(df) > days:
                df = df.tail(days)
                
            aligned_data[symbol] = pd.Series(df["price"].values, index=df["timestamp"])
        
        # Create a DataFrame with aligned timestamps
        correlation_df = pd.DataFrame(aligned_data)
        
        # Calculate correlation matrix
        corr_matrix = correlation_df.corr()
        
        # Create figure
        plt.figure(figsize=(10, 8))
        
        # Create heatmap
        sns.heatmap(
            corr_matrix,
            annot=True,
            cmap=color_scheme,
            linewidths=0.5,
            vmin=-1,
            vmax=1,
            annot_kws={"size": 10},
            fmt=".2f",
        )
        
        plt.title(f"Price Correlation Matrix - {days} Days", fontsize=16)
        plt.tight_layout()
        
        # Save the chart if requested
        output_path = ""
        if save:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            tokens_str = "_".join(list(data_frames.keys()))
            if len(tokens_str) > 50:
                tokens_str = f"{len(data_frames)}_tokens"
                
            filename = f"correlation_heatmap_{tokens_str}_{days}d_{timestamp}.png"
            output_path = os.path.join(self.comparison_charts_dir, filename)
            plt.savefig(output_path, dpi=300)
            logger.info(f"Correlation heatmap saved to {output_path}")
        
        # Show the chart if requested
        if show:
            plt.show()
        else:
            plt.close()
            
        return output_path 