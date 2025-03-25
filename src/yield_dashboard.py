#!/usr/bin/env python
"""
Yield Farming Dashboard for HiramAbiff

This module provides a web-based dashboard for yield farming opportunities
and portfolio management.
"""

import os
import time
import json
import argparse
from typing import Dict, List, Any, Optional
import logging
import random
from datetime import datetime, timedelta

# Dashboard Libraries
import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Import project modules
from src.data_aggregator import data_aggregator
from src.opportunity_detector import opportunity_detector
from src.trade_simulator import TradeSimulator, create_demo_portfolio
from src.yield_insights import YieldInsights

# Import the wallet dashboard components
from src.wallet_dashboard import create_wallet_dashboard, register_wallet_callbacks

# Global instances
trade_simulator = TradeSimulator()
yield_insights = YieldInsights()

# Dash app setup
def create_summary_cards(demo=False):
    """Create the summary cards for the dashboard."""
    # If in demo mode, get demo portfolio data
    if demo:
        portfolio = trade_simulator.get_portfolio_summary() if hasattr(trade_simulator, 'get_portfolio_summary') else {}
        portfolio_value = portfolio.get("total_value", 0)
        daily_yield = portfolio.get("daily_yield", 0)
        yearly_yield = portfolio.get("yearly_yield", 0)
        portfolio_change = portfolio.get("daily_change_percent", 0)
    else:
        # Use placeholder values
        portfolio_value = 0
        daily_yield = 0
        yearly_yield = 0
        portfolio_change = 0
    
    # Create the card layout
    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                # Total Portfolio Value
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Total Portfolio Value", className="card-subtitle text-muted"),
                            html.H3([
                                f"${portfolio_value:,.2f}",
                                html.Span(
                                    f" {portfolio_change:+.2f}%" if portfolio_change else "",
                                    className=f"ms-2 small {'text-success' if portfolio_change >= 0 else 'text-danger'}"
                                ),
                            ]),
                            html.P("Total value of assets in portfolio", className="card-text text-muted small"),
                        ])
                    ], className="h-100")
                ], md=6, lg=3, className="mb-3"),
                
                # Daily Yield
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Daily Yield", className="card-subtitle text-muted"),
                            html.H3([
                                f"${daily_yield:,.2f}",
                                html.Span(
                                    f" ({daily_yield / portfolio_value * 100:.2f}%)" if portfolio_value else "",
                                    className="ms-2 small text-muted"
                                ),
                            ]),
                            html.P("Estimated yield for the last 24 hours", className="card-text text-muted small"),
                        ])
                    ], className="h-100")
                ], md=6, lg=3, className="mb-3"),
                
                # Yearly Yield
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Annual Yield", className="card-subtitle text-muted"),
                            html.H3([
                                f"${yearly_yield:,.2f}",
                                html.Span(
                                    f" ({yearly_yield / portfolio_value * 100:.2f}%)" if portfolio_value else "",
                                    className="ms-2 small text-muted"
                                ),
                            ]),
                            html.P("Projected annual yield based on current rates", className="card-text text-muted small"),
                        ])
                    ], className="h-100")
                ], md=6, lg=3, className="mb-3"),
                
                # Opportunity Count
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H6("Active Opportunities", className="card-subtitle text-muted"),
                            html.H3([
                                f"{len(data_aggregator.fetch_solana_yields())}",
                                html.Span(
                                    " opportunities",
                                    className="ms-2 small text-muted"
                                ),
                            ]),
                            html.P("Yield farming opportunities currently available", className="card-text text-muted small"),
                        ])
                    ], className="h-100")
                ], md=6, lg=3, className="mb-3"),
            ]),
        ])
    ], className="mb-4 shadow-sm")

def create_portfolio_table(demo=False):
    """Create the portfolio table for the dashboard."""
    # Create the card layout
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Your Portfolio", className="mb-0"),
        ]),
        dbc.CardBody([
            html.Div(id="portfolio-table-container", children=[
                # This will be populated by a callback
                html.P("No portfolio data available. Connect your wallet or enable demo mode.", className="text-muted")
                if not demo else
                html.P("Loading portfolio data...", className="text-muted")
            ]),
            html.Div([
                dbc.Button("Refresh Portfolio", id="refresh-portfolio-btn", color="primary", className="mt-3"),
            ] if demo else [])
        ])
    ], className="mb-4 shadow-sm")

def create_opportunities_card(demo=False):
    """Create the opportunities card for the dashboard."""
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H5("Yield Farming Opportunities", className="mb-0 d-inline"),
                dbc.Button(
                    html.I(className="fas fa-sync-alt"),
                    id="refresh-opportunities-btn",
                    color="link",
                    size="sm",
                    className="float-end"
                ),
            ]),
        ]),
        dbc.CardBody([
            # Filters
            dbc.Row([
                dbc.Col([
                    html.Label("Protocol", className="small text-muted"),
                    dcc.Dropdown(
                        id="protocol-filter",
                        options=[
                            {"label": "All Protocols", "value": "all"},
                            {"label": "Raydium", "value": "raydium"},
                            {"label": "Orca", "value": "orca"},
                            {"label": "Marinade", "value": "marinade"},
                            {"label": "Solend", "value": "solend"},
                        ],
                        value="all",
                        clearable=False,
                        className="mb-3"
                    ),
                ], md=6, lg=4),
                dbc.Col([
                    html.Label("Token", className="small text-muted"),
                    dcc.Dropdown(
                        id="token-filter",
                        options=[
                            {"label": "All Tokens", "value": "all"},
                            {"label": "SOL", "value": "SOL"},
                            {"label": "USDC", "value": "USDC"},
                            {"label": "ETH", "value": "ETH"},
                            {"label": "BTC", "value": "BTC"},
                        ],
                        value="all",
                        clearable=False,
                        className="mb-3"
                    ),
                ], md=6, lg=4),
                dbc.Col([
                    html.Label("Min APY", className="small text-muted"),
                    dcc.Slider(
                        id="min-apy-slider",
                        min=0,
                        max=50,
                        step=1,
                        marks={i: f"{i}%" for i in range(0, 51, 10)},
                        value=0,
                        className="mb-3"
                    ),
                ], md=12, lg=4),
            ]),
            
            # Opportunities table
            html.Div(id="opportunities-table-container", children=[
                # This will be populated by a callback
                html.P("Loading yield farming opportunities...", className="text-muted")
            ]),
        ])
    ], className="shadow-sm h-100")

def create_analytics_card(demo=False):
    """Create the analytics card for the dashboard."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Analytics", className="mb-0"),
        ]),
        dbc.CardBody([
            # APY Distribution
            html.H6("APY Distribution", className="mb-3"),
            dcc.Graph(
                id="apy-distribution-chart",
                figure=px.bar(
                    x=["0-5%", "5-10%", "10-15%", "15-20%", "20%+"],
                    y=[8, 12, 6, 4, 2],
                    labels={"x": "APY Range", "y": "Number of Opportunities"},
                ).update_layout(
                    margin=dict(l=40, r=40, t=10, b=30),
                    height=200,
                ),
                config={"displayModeBar": False},
            ),
            
            # Protocol Distribution
            html.H6("Protocol Distribution", className="mt-4 mb-3"),
            dcc.Graph(
                id="protocol-distribution-chart",
                figure=px.pie(
                    values=[15, 12, 8, 5],
                    names=["Raydium", "Orca", "Marinade", "Solend"],
                ).update_layout(
                    margin=dict(l=40, r=40, t=10, b=30),
                    height=200,
                ),
                config={"displayModeBar": False},
            ),
            
            # Risk Analysis
            html.H6("Risk vs. Return", className="mt-4 mb-3"),
            dcc.Graph(
                id="risk-return-chart",
                figure=px.scatter(
                    x=[1, 2, 3, 4, 5, 2.5, 3.5, 4.5],
                    y=[5, 8, 12, 15, 20, 10, 18, 7],
                    labels={"x": "Risk Score (1-5)", "y": "APY (%)"},
                    size=[10, 15, 12, 8, 5, 10, 7, 9],
                ).update_layout(
                    margin=dict(l=40, r=40, t=10, b=30),
                    height=200,
                ),
                config={"displayModeBar": False},
            ),
        ])
    ], className="shadow-sm h-100")

def create_insights_card():
    """Create the AI-powered insights card for the dashboard."""
    return dbc.Card([
        dbc.CardHeader([
            html.Div([
                html.H5("AI-Powered Analysis", className="mb-0 d-inline"),
                dbc.Button(
                    html.I(className="fas fa-lightbulb"),
                    id="refresh-insights-btn",
                    color="link",
                    size="sm",
                    className="float-end"
                ),
            ]),
        ]),
        dbc.CardBody([
            # Insight categories
            dbc.Tabs([
                dbc.Tab([
                    html.Div(id="market-trends-content", children=[
                        html.P("Getting the latest market trends...", className="text-muted"),
                        dbc.Spinner(color="primary", size="sm"),
                    ]),
                ], label="Market Trends", tab_id="tab-market-trends"),
                dbc.Tab([
                    html.Div(id="risk-insights-content", children=[
                        html.P("Analyzing risk-reward ratios...", className="text-muted"),
                        dbc.Spinner(color="primary", size="sm"),
                    ]),
                ], label="Risk Analysis", tab_id="tab-risk-analysis"),
                dbc.Tab([
                    html.Div(id="portfolio-insights-content", children=[
                        html.P("Analyzing your portfolio...", className="text-muted"),
                        dbc.Spinner(color="primary", size="sm"),
                    ]),
                ], label="Portfolio Analysis", tab_id="tab-portfolio-analysis"),
            ], id="insights-tabs", active_tab="tab-market-trends"),
        ])
    ], className="shadow-sm h-100")

def create_charts_card():
    """Create the charts card for the dashboard."""
    return dbc.Card([
        dbc.CardHeader([
            html.H5("Performance Charts", className="mb-0"),
        ]),
        dbc.CardBody([
            # Chart selector
            dbc.RadioItems(
                id="chart-time-selector",
                options=[
                    {"label": "1D", "value": "1d"},
                    {"label": "1W", "value": "1w"},
                    {"label": "1M", "value": "1m"},
                    {"label": "3M", "value": "3m"},
                    {"label": "1Y", "value": "1y"},
                ],
                value="1m",
                inline=True,
                className="mb-3"
            ),
            
            # Performance chart
            dcc.Graph(
                id="performance-chart",
                figure=px.line(
                    x=[f"2023-{i:02d}-01" for i in range(1, 13)],
                    y=[10000, 10250, 10400, 10800, 11200, 11500, 12000, 12300, 12500, 12700, 13000, 13500],
                    labels={"x": "Date", "y": "Portfolio Value ($)"},
                ).update_layout(
                    margin=dict(l=40, r=40, t=10, b=30),
                    height=300,
                ),
                config={"displayModeBar": False},
            ),
            
            # Comparison chart
            html.H6("Performance vs. Benchmarks", className="mt-4 mb-3"),
            dcc.Graph(
                id="comparison-chart",
                figure=px.line(
                    x=[f"2023-{i:02d}-01" for i in range(1, 13)],
                    y=[
                        [5, 8, 12, 15, 18, 20, 25, 28, 30, 32, 35, 40],  # Your portfolio
                        [3, 5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25],    # SOL
                        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],         # S&P 500
                    ],
                    labels={"x": "Date", "y": "Return (%)"},
                ).update_layout(
                    margin=dict(l=40, r=40, t=10, b=30),
                    height=200,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    ),
                ),
                config={"displayModeBar": False},
            ),
        ])
    ], className="shadow-sm h-100")

def register_callbacks(app, demo=False):
    """
    Register callbacks for the dashboard.
    
    Args:
        app: The Dash app
        demo: Whether to use demo mode with pre-populated portfolio
    """
    # Update portfolio table
    @app.callback(
        Output("portfolio-table-container", "children"),
        [Input("refresh-portfolio-btn", "n_clicks")],
        prevent_initial_call=False
    )
    def update_portfolio_table(n_clicks):
        if not demo:
            return html.P("No portfolio data available. Connect your wallet or enable demo mode.", className="text-muted")
        
        # Get demo portfolio data
        portfolio_data = trade_simulator.get_portfolio_summary() if hasattr(trade_simulator, 'get_portfolio_summary') else {}
        
        if not portfolio_data:
            return html.P("No portfolio data available.", className="text-muted")
        
        # Extract strategies
        strategies = portfolio_data.get("strategies", [])
        
        if not strategies:
            return html.P("No active strategies in portfolio.", className="text-muted")
        
        # Create table
        table = dash.dash_table.DataTable(
            id='portfolio-table',
            columns=[
                {"name": "Strategy", "id": "name"},
                {"name": "Protocol", "id": "protocol"},
                {"name": "Asset", "id": "symbol"},
                {"name": "Investment", "id": "investment"},
                {"name": "Value", "id": "value"},
                {"name": "Yield", "id": "yield"},
                {"name": "APY", "id": "apy"},
                {"name": "Risk", "id": "risk"},
            ],
            data=[
                {
                    "name": strategy.get("name", "Unknown"),
                    "protocol": strategy.get("protocol", "Unknown"),
                    "symbol": strategy.get("symbol", "Unknown"),
                    "investment": f"${strategy.get('initial_investment', 0):,.2f}",
                    "value": f"${strategy.get('current_value', 0):,.2f}",
                    "yield": f"${strategy.get('profit', 0):,.2f}",
                    "apy": f"{strategy.get('apy', 0):.2f}%",
                    "risk": strategy.get("risk_level", "Unknown"),
                }
                for strategy in strategies
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'minWidth': '80px',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                }
            ],
            style_as_list_view=True,
        )
        
        return table
    
    # Update opportunities table
    @app.callback(
        Output("opportunities-table-container", "children"),
        [Input("refresh-opportunities-btn", "n_clicks"),
         Input("protocol-filter", "value"),
         Input("token-filter", "value"),
         Input("min-apy-slider", "value")],
        prevent_initial_call=False
    )
    def update_opportunities_table(n_clicks, protocol_filter, token_filter, min_apy):
        # Get opportunities from data_aggregator
        opportunities = data_aggregator.fetch_solana_yields()
        
        if not opportunities:
            return html.P("No yield farming opportunities available.", className="text-muted")
        
        # Apply filters
        filtered_opps = opportunities.copy()
        
        if protocol_filter and protocol_filter != "all":
            filtered_opps = [opp for opp in filtered_opps if opp.get("project", "").lower() == protocol_filter.lower()]
        
        if token_filter and token_filter != "all":
            filtered_opps = [opp for opp in filtered_opps if token_filter.upper() in opp.get("symbol", "").upper()]
        
        if min_apy is not None:
            filtered_opps = [opp for opp in filtered_opps if opp.get("apy", 0) >= min_apy]
        
        # Sort by APY descending
        filtered_opps = sorted(filtered_opps, key=lambda opp: opp.get("apy", 0), reverse=True)
        
        # Limit to top 20
        filtered_opps = filtered_opps[:20]
        
        # Create table
        if not filtered_opps:
            return html.P("No opportunities match the selected filters.", className="text-muted")
        
        table = dash.dash_table.DataTable(
            id='opportunities-table',
            columns=[
                {"name": "Protocol", "id": "project"},
                {"name": "Pool", "id": "symbol"},
                {"name": "APY", "id": "apy"},
                {"name": "TVL", "id": "tvlUsd"},
                {"name": "Risk", "id": "risk_level"},
                {"name": "Action", "id": "action"},
            ],
            data=[
                {
                    "project": opp.get("project", "Unknown"),
                    "symbol": opp.get("symbol", "Unknown"),
                    "apy": f"{opp.get('apy', 0):.2f}%",
                    "tvlUsd": f"${opp.get('tvlUsd', 0)/1000000:.2f}M",
                    "risk_level": opp.get("risk_level", "Medium"),
                    "action": "Simulate",
                }
                for opp in filtered_opps
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'minWidth': '80px',
            },
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': 'rgb(248, 248, 248)'
                },
                {
                    'if': {'column_id': 'action'},
                    'cursor': 'pointer',
                    'color': 'blue',
                    'textDecoration': 'underline'
                }
            ],
            style_as_list_view=True,
            sort_action="native",
            sort_mode="multi",
            filter_action="native",
        )
        
        return table
    
    # Update AI-powered insights
    @app.callback(
        [Output("market-trends-content", "children"),
         Output("risk-insights-content", "children"),
         Output("portfolio-insights-content", "children")],
        [Input("refresh-insights-btn", "n_clicks")],
        prevent_initial_call=False
    )
    def update_insights(n_clicks):
        # Market Trends
        try:
            market_trends = yield_insights.generate_market_trends()
            market_trends_content = html.Div([
                html.P(market_trends, className="insights-text")
            ])
        except Exception as e:
            market_trends_content = html.Div([
                html.P(f"Error generating market trends: {str(e)}", className="text-danger")
            ])
        
        # Risk Analysis
        try:
            risk_analysis = yield_insights.generate_risk_analysis()
            risk_content = html.Div([
                html.P(risk_analysis, className="insights-text")
            ])
        except Exception as e:
            risk_content = html.Div([
                html.P(f"Error generating risk analysis: {str(e)}", className="text-danger")
            ])
        
        # Portfolio Analysis
        try:
            if demo:
                portfolio_data = trade_simulator.get_portfolio_summary() if hasattr(trade_simulator, 'get_portfolio_summary') else {}
                portfolio_analysis = yield_insights.generate_portfolio_analysis(portfolio_data)
                portfolio_content = html.Div([
                    html.P(portfolio_analysis, className="insights-text")
                ])
            else:
                portfolio_content = html.Div([
                    html.P("Connect your wallet or enable demo mode to see portfolio insights.", className="text-muted")
                ])
        except Exception as e:
            portfolio_content = html.Div([
                html.P(f"Error generating portfolio analysis: {str(e)}", className="text-danger")
            ])
        
        return market_trends_content, risk_content, portfolio_content

def create_dashboard(demo=False):
    """
    Create the yield farming dashboard.

    Args:
        demo: Whether to use demo mode (with pre-populated portfolio)

    Returns:
        dash.Dash: The dashboard application
    """
    # Create the app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP, "/static/css/styles.css"],
        title="HiramAbiff Yield Farming Dashboard",
        suppress_callback_exceptions=True,
        server=False,
    )

    # Main layout
    app.layout = html.Div([
        html.Div([
            # Meta tags for viewport and theme color
            html.Meta(name="viewport", content="width=device-width, initial-scale=1.0"),
            html.Meta(name="theme-color", content="#7B68EE"),
            
            # External stylesheets
            html.Link(
                rel="stylesheet",
                href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css"
            ),
            
            # Navbar
            dbc.Navbar(
                dbc.Container([
                    dbc.Row([
                        dbc.Col([
                            html.I(className="fas fa-coins me-2"),
                            html.Span("HiramAbiff", className="navbar-brand-text"),
                        ], width="auto"),
                    ], className="g-0"),
                    dbc.Row([
                        dbc.Col([
                            dbc.NavItem(dbc.NavLink("Dashboard", href="#", active=True)),
                            dbc.NavItem(dbc.NavLink("Wallet", href="#wallet-section")),
                            dbc.NavItem(dbc.NavLink("Market", href="#", external_link=True, target="_blank")),
                            dbc.NavItem(dbc.NavLink("Settings", href="#")),
                        ], className="d-none d-md-flex"),
                    ], className="g-0"),
                ]),
                color="dark",
                dark=True,
                className="mb-4",
            ),
            
            # Main content
            dbc.Container([
                # Tabs 
                dbc.Tabs([
                    dbc.Tab([
                        dbc.Row([
                            dbc.Col([
                                # Summary cards
                                create_summary_cards(demo),
                                html.Div(id="portfolio-performance"),
                                # Portfolio table
                                create_portfolio_table(demo),
                            ], width=12),
                        ]),
                        
                        # Opportunities & Analytics row
                        dbc.Row([
                            dbc.Col([
                                create_opportunities_card(demo),
                            ], lg=8),
                            dbc.Col([
                                create_analytics_card(demo),
                            ], lg=4),
                        ], className="mt-4"),
                        
                        # AI-powered analysis & Charts row
                        dbc.Row([
                            dbc.Col([
                                create_insights_card(),
                            ], lg=6),
                            dbc.Col([
                                create_charts_card(),
                            ], lg=6),
                        ], className="mt-4"),
                    ], label="Dashboard", tab_id="tab-dashboard"),
                    
                    # New tab for wallet integration
                    dbc.Tab(
                        create_wallet_dashboard(),
                        label="Wallet Integration",
                        tab_id="tab-wallet",
                        id="wallet-section"
                    ),
                ], id="dashboard-tabs", active_tab="tab-dashboard"),
                
                # Footer
                html.Footer([
                    html.P([
                        "© 2023 HiramAbiff - Solana Yield Farming Dashboard. ",
                        html.A("Terms of Service", href="#"),
                        " | ",
                        html.A("Privacy Policy", href="#"),
                    ]),
                ], className="mt-5 pt-4 border-top text-center text-muted"),
                
                # Hidden divs for storing data
                html.Div(id='opportunity-click-data', style={'display': 'none'}),
                
            ], className="pt-4"),
        ], id="main-container", className="bg-light"),
        
        # Intermediate div for clientside callbacks
        html.Div(id="clientside-store", style={"display": "none"}),
    ])
    
    # Register callbacks
    register_callbacks(app, demo)
    register_wallet_callbacks(app)
    
    return app

# Main entry point
if __name__ == "__main__":
    import argparse
    from pathlib import Path
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="HiramAbiff Yield Dashboard")
    parser.add_argument("--port", type=int, default=8889, help="Port to run the dashboard on")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()
    
    # Create cache directories
    CACHE_DIR = Path("cache")
    CACHE_DIR.mkdir(exist_ok=True)
    Path("portfolios").mkdir(exist_ok=True)
    
    # Initialize with demo portfolio
    create_demo_portfolio()
    
    # Create the dashboard app
    app = create_dashboard(demo=args.demo)
    
    # Run the app
    app.run(debug=args.debug, port=args.port) 