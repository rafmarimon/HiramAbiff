"""
Wallet Dashboard Components for HiramAbiff

This module provides Dash components for wallet integration and portfolio tracking.
"""

import os
import json
from typing import Dict, List, Any, Optional
import datetime

import dash
from dash import dcc, html, callback, Input, Output, State, ClientsideFunction
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px

from src.blockchain.wallet_integration import wallet_integration
from src.monetization.fee_manager import fee_manager

# Wallet connection card
def create_wallet_card():
    """Create a card for wallet connection."""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Connect Wallet", className="mb-0"),
        ]),
        dbc.CardBody([
            html.Div([
                html.P("Connect your Solana wallet to track your portfolio and interact with yield opportunities."),
                html.Div([
                    dbc.Button("Connect Phantom", id="connect-phantom-btn", color="primary", className="me-2"),
                    dbc.Button("Connect Solflare", id="connect-solflare-btn", color="primary"),
                ], className="mb-3"),
                html.Div(id="wallet-connection-status"),
                html.Div(id="wallet-data-store", style={"display": "none"}),
                
                # Hidden div for wallet connection data
                html.Div(id="wallet-connection-data", style={"display": "none"}),
                
                # Clientside callbacks for wallet connection
                dcc.ClientsideFunction(
                    namespace="wallet",
                    function_name="connectPhantom",
                    id="clientside-phantom"
                ),
                dcc.ClientsideFunction(
                    namespace="wallet",
                    function_name="connectSolflare",
                    id="clientside-solflare"
                ),
                dcc.ClientsideFunction(
                    namespace="wallet",
                    function_name="disconnectWallet",
                    id="clientside-disconnect"
                ),
            ])
        ])
    ], className="mb-4")

# Wallet portfolio card
def create_portfolio_card():
    """Create a card for wallet portfolio."""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Your Portfolio", className="mb-0"),
        ]),
        dbc.CardBody([
            html.Div(id="portfolio-content", children=[
                html.P("Connect your wallet to view your portfolio.", className="text-muted"),
            ])
        ])
    ], className="mb-4")

# Staked assets card
def create_staked_assets_card():
    """Create a card for staked assets."""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Staked Assets", className="mb-0"),
        ]),
        dbc.CardBody([
            html.Div(id="staked-assets-content", children=[
                html.P("Connect your wallet to view your staked assets.", className="text-muted"),
            ])
        ])
    ], className="mb-4")

# Transaction history card
def create_transaction_history_card():
    """Create a card for transaction history."""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Transaction History", className="mb-0"),
        ]),
        dbc.CardBody([
            html.Div(id="transaction-history-content", children=[
                html.P("Connect your wallet to view your transaction history.", className="text-muted"),
            ])
        ])
    ], className="mb-4")

# HIRAM token staking card
def create_token_staking_card():
    """Create a card for HIRAM token staking."""
    hiram_token = fee_manager.get_token_info()
    
    return dbc.Card([
        dbc.CardHeader([
            html.H4(f"Stake {hiram_token['symbol']} Tokens", className="mb-0"),
        ]),
        dbc.CardBody([
            html.Div([
                html.P([
                    f"Stake {hiram_token['symbol']} tokens to earn {hiram_token['staking_apy']}% APY ",
                    "and reduce your platform fees."
                ]),
                html.Div([
                    html.H5("Current Price", className="mb-2"),
                    html.P([
                        f"${hiram_token['current_price_usd']:.2f} per {hiram_token['symbol']}",
                    ], className="mb-3"),
                    html.H5("Fee Discount Tiers", className="mb-2"),
                    html.Ul([
                        html.Li(f"1,000 {hiram_token['symbol']} = 0.1% fee discount"),
                        html.Li(f"10,000 {hiram_token['symbol']} = 1% fee discount"),
                        html.Li(f"100,000 {hiram_token['symbol']} = 10% fee discount"),
                        html.Li(f"500,000 {hiram_token['symbol']} = 50% fee discount (max)"),
                    ], className="mb-3"),
                    html.H5("Stake Tokens", className="mb-2"),
                    dbc.InputGroup([
                        dbc.Input(id="stake-amount-input", type="number", placeholder="Amount to stake"),
                        dbc.InputGroupText(hiram_token['symbol']),
                    ], className="mb-2"),
                    dbc.Button("Stake Tokens", id="stake-tokens-btn", color="success", disabled=True, className="me-2"),
                    dbc.Button("Unstake Tokens", id="unstake-tokens-btn", color="danger", disabled=True),
                ], className="mt-3"),
                html.Div(id="staking-message", className="mt-3"),
            ])
        ])
    ], className="mb-4")

# Fee information card
def create_fee_info_card():
    """Create a card for fee information."""
    return dbc.Card([
        dbc.CardHeader([
            html.H4("Fee Information", className="mb-0"),
        ]),
        dbc.CardBody([
            html.Div([
                html.P([
                    "HiramAbiff charges a small fee of 1% on profits from yield farming opportunities. ",
                    "This fee is only charged when you make a profit, and you can reduce it by staking HIRAM tokens."
                ]),
                html.Div([
                    html.H5("Your Fee Stats", className="mb-2"),
                    html.Div(id="fee-stats-content", children=[
                        html.P("Connect your wallet to view your fee stats.", className="text-muted"),
                    ]),
                ], className="mt-3"),
            ])
        ])
    ], className="mb-4")

# Create the complete wallet dashboard
def create_wallet_dashboard():
    """Create the complete wallet dashboard."""
    return html.Div([
        html.Div([
            html.H2("Wallet Integration", className="mb-4"),
            html.P([
                "Connect your Solana wallet to track your portfolio, view your staked assets, ",
                "and interact with yield opportunities."
            ], className="mb-4"),
        ], className="mb-4"),
        
        html.Div([
            dbc.Row([
                dbc.Col([
                    create_wallet_card(),
                    create_portfolio_card(),
                ], width=6),
                dbc.Col([
                    create_staked_assets_card(),
                    create_transaction_history_card(),
                ], width=6),
            ]),
            
            html.H3("Monetization Features", className="my-4"),
            dbc.Row([
                dbc.Col([
                    create_token_staking_card(),
                ], width=6),
                dbc.Col([
                    create_fee_info_card(),
                ], width=6),
            ]),
        ]),
        
        # JavaScript for wallet connection
        html.Script(src="/static/js/wallet_connector.js"),
    ])

# Callback to connect Phantom wallet
def register_wallet_callbacks(app):
    """Register wallet-related callbacks."""
    
    # Connect Phantom wallet
    app.clientside_callback(
        ClientsideFunction(namespace="hiramWallet", function_name="connectPhantom"),
        Output("wallet-connection-data", "children"),
        Input("connect-phantom-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    
    # Process wallet connection
    @app.callback(
        [
            Output("wallet-connection-status", "children"),
            Output("wallet-data-store", "children"),
            Output("stake-tokens-btn", "disabled"),
            Output("unstake-tokens-btn", "disabled"),
        ],
        Input("wallet-connection-data", "children"),
        prevent_initial_call=True,
    )
    def process_wallet_connection(connection_data):
        """Process wallet connection data."""
        if connection_data is None:
            return (
                html.P("No wallet connected", className="text-muted"),
                "",
                True,
                True
            )
        
        try:
            data = json.loads(connection_data)
            
            if data.get("success", False):
                # Process successful connection
                wallet_type = data.get("walletType", "unknown")
                public_key = data.get("publicKey", "")
                
                # Connect in backend
                success, message = wallet_integration.connect_wallet(wallet_type)
                
                if success:
                    return (
                        html.Div([
                            html.P([
                                f"Connected to {wallet_type.capitalize()} wallet: ",
                                html.Span(public_key[:8] + "..." + public_key[-4:], className="font-monospace"),
                            ], className="text-success mb-2"),
                            dbc.Button("Disconnect", id="disconnect-wallet-btn", color="outline-danger", size="sm"),
                        ]),
                        json.dumps({"publicKey": public_key, "walletType": wallet_type}),
                        False,
                        False
                    )
                else:
                    return (
                        html.P(f"Error: {message}", className="text-danger"),
                        "",
                        True,
                        True
                    )
            else:
                return (
                    html.P(f"Error: {data.get('message', 'Unknown error')}", className="text-danger"),
                    "",
                    True,
                    True
                )
        except Exception as e:
            return (
                html.P(f"Error: {str(e)}", className="text-danger"),
                "",
                True,
                True
            )
    
    # Disconnect wallet
    app.clientside_callback(
        ClientsideFunction(namespace="hiramWallet", function_name="disconnectWallet"),
        Output("wallet-connection-data", "children", allow_duplicate=True),
        Input("disconnect-wallet-btn", "n_clicks"),
        State("wallet-data-store", "children"),
        prevent_initial_call=True,
    )
    
    # Update portfolio content
    @app.callback(
        Output("portfolio-content", "children"),
        Input("wallet-data-store", "children"),
        prevent_initial_call=True,
    )
    def update_portfolio_content(wallet_data):
        """Update portfolio content based on wallet data."""
        if not wallet_data:
            return html.P("Connect your wallet to view your portfolio.", className="text-muted")
        
        try:
            # Get wallet data from integration
            data = wallet_integration.get_wallet_data()
            
            if "error" in data:
                return html.P(f"Error: {data['error']}", className="text-danger")
            
            # Calculate total value
            total_value = sum(token.get("value_usd", 0) for token in data.get("tokens", []))
            
            # Create token table
            token_rows = []
            for token in data.get("tokens", []):
                token_rows.append(
                    html.Tr([
                        html.Td(token.get("symbol", "")),
                        html.Td(f"{token.get('amount', 0):,.2f}"),
                        html.Td(f"${token.get('value_usd', 0):,.2f}"),
                        html.Td(f"{token.get('value_usd', 0) / total_value * 100:.1f}%")
                    ])
                )
            
            return html.Div([
                html.H5("Wallet Balance", className="mb-3"),
                html.P(f"Total Value: ${total_value:,.2f}", className="h4 text-primary mb-3"),
                html.Div([
                    html.Table([
                        html.Thead(
                            html.Tr([
                                html.Th("Token"),
                                html.Th("Amount"),
                                html.Th("Value (USD)"),
                                html.Th("Allocation")
                            ])
                        ),
                        html.Tbody(token_rows)
                    ], className="table table-striped table-sm")
                ])
            ])
        except Exception as e:
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    # Update staked assets content
    @app.callback(
        Output("staked-assets-content", "children"),
        Input("wallet-data-store", "children"),
        prevent_initial_call=True,
    )
    def update_staked_assets_content(wallet_data):
        """Update staked assets content based on wallet data."""
        if not wallet_data:
            return html.P("Connect your wallet to view your staked assets.", className="text-muted")
        
        try:
            # Get wallet data from integration
            data = wallet_integration.get_wallet_data()
            
            if "error" in data:
                return html.P(f"Error: {data['error']}", className="text-danger")
            
            # Calculate total staked value
            staked_assets = data.get("staked", [])
            total_staked = sum(asset.get("value_usd", 0) for asset in staked_assets)
            
            if not staked_assets:
                return html.P("You don't have any staked assets yet.", className="text-muted")
            
            # Create staked assets table
            staked_rows = []
            for asset in staked_assets:
                staked_rows.append(
                    html.Tr([
                        html.Td(asset.get("protocol", "")),
                        html.Td(asset.get("symbol", "")),
                        html.Td(f"{asset.get('amount', 0):,.2f}"),
                        html.Td(f"${asset.get('value_usd', 0):,.2f}"),
                        html.Td(f"{asset.get('apy', 0):,.2f}%")
                    ])
                )
            
            # Calculate annual yield
            annual_yield = sum(asset.get("value_usd", 0) * asset.get("apy", 0) / 100 for asset in staked_assets)
            
            return html.Div([
                html.H5("Staked Assets", className="mb-3"),
                html.P([
                    f"Total Staked: ${total_staked:,.2f} | ",
                    f"Est. Annual Yield: ${annual_yield:,.2f}"
                ], className="h5 text-success mb-3"),
                html.Div([
                    html.Table([
                        html.Thead(
                            html.Tr([
                                html.Th("Protocol"),
                                html.Th("Asset"),
                                html.Th("Amount"),
                                html.Th("Value (USD)"),
                                html.Th("APY")
                            ])
                        ),
                        html.Tbody(staked_rows)
                    ], className="table table-striped table-sm")
                ])
            ])
        except Exception as e:
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    # Update transaction history content
    @app.callback(
        Output("transaction-history-content", "children"),
        Input("wallet-data-store", "children"),
        prevent_initial_call=True,
    )
    def update_transaction_history_content(wallet_data):
        """Update transaction history content based on wallet data."""
        if not wallet_data:
            return html.P("Connect your wallet to view your transaction history.", className="text-muted")
        
        try:
            # Get wallet data from integration
            data = wallet_integration.get_wallet_data()
            
            if "error" in data:
                return html.P(f"Error: {data['error']}", className="text-danger")
            
            # Get transactions
            transactions = data.get("transactions", [])
            
            if not transactions:
                return html.P("No transactions found.", className="text-muted")
            
            # Create transaction table
            tx_rows = []
            for tx in transactions:
                tx_rows.append(
                    html.Tr([
                        html.Td(tx.get("type", "")),
                        html.Td(tx.get("protocol", "")),
                        html.Td(f"{tx.get('amount', 0):,.2f}"),
                        html.Td(tx.get("timestamp", "").split("T")[0]),
                        html.Td(tx.get("status", ""))
                    ])
                )
            
            return html.Div([
                html.H5("Transaction History", className="mb-3"),
                html.Div([
                    html.Table([
                        html.Thead(
                            html.Tr([
                                html.Th("Type"),
                                html.Th("Protocol"),
                                html.Th("Amount"),
                                html.Th("Date"),
                                html.Th("Status")
                            ])
                        ),
                        html.Tbody(tx_rows)
                    ], className="table table-striped table-sm")
                ])
            ])
        except Exception as e:
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    # Handle token staking
    @app.callback(
        Output("staking-message", "children"),
        Input("stake-tokens-btn", "n_clicks"),
        State("stake-amount-input", "value"),
        State("wallet-data-store", "children"),
        prevent_initial_call=True,
    )
    def handle_stake_tokens(n_clicks, amount, wallet_data):
        """Handle token staking."""
        if not wallet_data or not amount:
            return ""
        
        try:
            wallet_data = json.loads(wallet_data)
            wallet_address = wallet_data.get("publicKey", "")
            
            if not wallet_address:
                return html.P("No wallet connected.", className="text-danger")
            
            # Call the fee manager to stake tokens
            result = fee_manager.stake_tokens(wallet_address, float(amount))
            
            if "error" in result:
                return html.P(f"Error: {result['error']}", className="text-danger")
            
            return html.P(f"Successfully staked {amount:,.2f} HIRAM tokens!", className="text-success")
        except Exception as e:
            return html.P(f"Error: {str(e)}", className="text-danger")
    
    # Update fee stats content
    @app.callback(
        Output("fee-stats-content", "children"),
        Input("wallet-data-store", "children"),
        prevent_initial_call=True,
    )
    def update_fee_stats_content(wallet_data):
        """Update fee stats content based on wallet data."""
        if not wallet_data:
            return html.P("Connect your wallet to view your fee stats.", className="text-muted")
        
        try:
            wallet_data = json.loads(wallet_data)
            wallet_address = wallet_data.get("publicKey", "")
            
            # Get fee stats
            stats = fee_manager.get_fee_stats(wallet_address)
            
            # Get staking info for discount
            staking_info = fee_manager.get_staking_info(wallet_address)
            
            # Calculate fee discount
            discount = fee_manager.get_fee_discount_for_staking(wallet_address)
            effective_fee = max(0, fee_manager.default_fee_percent - discount)
            
            return html.Div([
                html.Div([
                    html.P([
                        "Base Fee Rate: ",
                        html.Span(f"{fee_manager.default_fee_percent:.2f}%", className="fw-bold"),
                    ]),
                    html.P([
                        "Your Discount: ",
                        html.Span(f"{discount:.2f}%", className="fw-bold text-success"),
                        " (based on staked HIRAM)"
                    ]),
                    html.P([
                        "Effective Fee Rate: ",
                        html.Span(f"{effective_fee:.2f}%", className="fw-bold text-primary"),
                    ]),
                ], className="mb-3"),
                
                html.Hr(),
                
                html.Div([
                    html.P([
                        "Total Profit: ",
                        html.Span(f"${stats.get('total_profit', 0):,.2f}", className="fw-bold"),
                    ]),
                    html.P([
                        "Total Fees Paid: ",
                        html.Span(f"${stats.get('total_fees', 0):,.2f}", className="fw-bold"),
                    ]),
                    html.P([
                        "Transactions: ",
                        html.Span(f"{stats.get('num_transactions', 0)}", className="fw-bold"),
                    ]),
                ], className="mb-3"),
            ])
        except Exception as e:
            return html.P(f"Error: {str(e)}", className="text-danger") 