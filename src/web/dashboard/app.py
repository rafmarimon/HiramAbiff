"""
Dashboard application for HiramAbiff.

This module provides a Dash-based web dashboard for HiramAbiff.
"""

import datetime
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import re

import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from loguru import logger

from src.core.config import settings
from src.agents.langchain_agent import market_analysis_agent


def create_dashboard() -> dash.Dash:
    """
    Create and configure the Dash application.
    
    Returns:
        dash.Dash: The configured Dash application
    """
    # Create Dash app with Bootstrap
    app = dash.Dash(
        __name__,
        external_stylesheets=[
            dbc.themes.BOOTSTRAP,
            "/static/css/custom.css",
            "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",
            "https://use.fontawesome.com/releases/v5.15.4/css/all.css"
        ],
        external_scripts=[
            "/static/js/dashboard.js"
        ],
        suppress_callback_exceptions=True,
        title="HiramAbiff Dashboard",
        url_base_pathname="/dashboard/",
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ]
    )
    
    # Layout
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
        
        # Content
        dcc.Location(id="url", refresh=False),
        dbc.Container(
            html.Div(id="page-content", style={"padding": "20px"}),
            fluid=True,
            className="px-4"
        ),
        
        # Footer
        html.Footer(
            dbc.Container([
                dbc.Row([
                    dbc.Col(
                        html.P(
                            [
                                html.Span(f"HiramAbiff v0.1.0 - © {datetime.datetime.now().year} "),
                                html.A("Documentation", href="#", className="text-decoration-none ms-2"),
                                html.Span(" | "),
                                html.A("GitHub", href="#", className="text-decoration-none"),
                                html.Span(" | "),
                                html.A("Support", href="#", className="text-decoration-none"),
                            ],
                            className="text-center text-muted mb-0"
                        ),
                        width=12
                    )
                ])
            ]),
            style={"padding": "20px", "marginTop": "50px"}
        ),
        
        # Interval component for periodic updates
        dcc.Interval(
            id="interval-component",
            interval=60 * 1000,  # in milliseconds (1 minute)
            n_intervals=0
        ),
    ])
    
    # Add all the callbacks
    _setup_callbacks(app)
    
    return app


def _setup_callbacks(app: dash.Dash) -> None:
    """
    Set up all callbacks for the dashboard.
    
    Args:
        app: The Dash application
    """
    @app.callback(
        Output("page-content", "children"),
        Input("url", "pathname")
    )
    def render_page_content(pathname: str):
        """Render the page content based on the URL."""
        if pathname == "/dashboard/" or pathname == "/dashboard":
            return render_overview_page()
        elif pathname == "/dashboard/market-analysis":
            return render_market_analysis_page()
        elif pathname == "/dashboard/wallet-info":
            return render_wallet_info_page()
        elif pathname == "/dashboard/settings":
            return render_settings_page()
        else:
            # 404 page
            return html.Div([
                html.H1("404: Page Not Found", className="text-danger"),
                html.P(f"The path {pathname} was not found."),
                dbc.Button("Go to Overview", href="/dashboard/", color="primary")
            ], className="text-center")
    
    @app.callback(
        Output("market-analysis-content", "children"),
        [Input("generate-report-button", "n_clicks"), 
         Input("interval-component", "n_intervals")],
        State("market-analysis-content", "children"),
        prevent_initial_call=True
    )
    def generate_or_update_report(n_clicks, n_intervals, current_content):
        """Generate a new market analysis report on button click or update existing content."""
        ctx = dash.callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        
        if trigger_id == "generate-report-button" and n_clicks:
            loading_message = [
                html.Div([
                    html.H4([
                        html.I(className="fas fa-sync fa-spin me-2"),
                        "Generating new report..."
                    ]),
                    dbc.Spinner(size="lg", color="primary", className="my-3"),
                    html.P("This may take a few moments. The AI is analyzing market data...")
                ], className="text-center my-5 animate-on-scroll")
            ]
            
            # Trigger the agent to generate a report (in a real app)
            try:
                # In a real implementation, we would call the agent
                # asyncio.create_task(market_analysis_agent.generate_market_analysis())
                logger.info("Report generation triggered from dashboard")
                pass
            except Exception as e:
                logger.error(f"Error triggering report generation: {e}")
            
            return loading_message
        
        # For interval updates or first load, check for reports
        try:
            reports_dir = Path(settings.REPORTS_DIR)
            if not reports_dir.exists():
                reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Get the latest report file
            report_files = sorted(list(reports_dir.glob("*.txt")), key=lambda x: x.stat().st_mtime, reverse=True)
            
            if not report_files:
                return [
                    html.Div([
                        html.I(className="fas fa-file-alt fa-3x text-muted mb-3"),
                        html.H4("No reports available", className="text-muted"),
                        html.P("Click the button above to generate your first market analysis report"),
                    ], className="text-center my-5 animate-on-scroll")
                ]
            
            latest_report = report_files[0]
            report_time = datetime.datetime.fromtimestamp(latest_report.stat().st_mtime)
            report_content = latest_report.read_text()
            
            # Parse the content for better formatting
            sections = []
            current_section = {"title": "Summary", "content": []}
            
            for line in report_content.split('\n'):
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
            
            if not sections:
                sections = [{"title": "Market Analysis", "content": report_content.split('\n')}]
            
            # Format the report with cards for each section
            report_components = [
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    f"Report generated on {report_time.strftime('%B %d, %Y at %H:%M')}",
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
            
            return report_components
            
        except Exception as e:
            logger.error(f"Error displaying report: {e}")
            return html.Div([
                html.I(className="fas fa-exclamation-triangle fa-2x text-warning mb-3"),
                html.H4("Error Displaying Report", className="text-warning"),
                html.P(f"Error: {str(e)}", className="text-muted"),
            ], className="text-center my-5 animate-on-scroll")
    
    @app.callback(
        Output("report-generation-status", "children"),
        Input("generate-report-button", "n_clicks"),
        prevent_initial_call=True
    )
    async def trigger_report_generation(n_clicks):
        """Trigger the generation of a new market analysis report."""
        if not n_clicks:
            return ""
        
        try:
            # Generate a new report
            await market_analysis_agent.generate_market_analysis()
            return html.Div("Report generated successfully!", className="text-success mt-2")
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return html.Div(f"Error generating report: {str(e)}", className="text-danger mt-2")

    @app.callback(
        Output("temperature-value", "children"),
        Input("llm-temperature", "value")
    )
    def update_temperature_display(value):
        """Update the displayed temperature value when slider moves."""
        return value

    @app.callback(
        Output("api-keys-save-status", "children"),
        [Input("save-api-keys-button", "n_clicks")],
        [State("openai-api-key", "value"),
         State("alchemy-api-key", "value"),
         State("alchemy-solana-url", "value"),
         State("langchain-api-key", "value")],
        prevent_initial_call=True
    )
    def handle_api_keys_save(n_clicks, openai_key, alchemy_key, alchemy_solana_url, langchain_key):
        """Handle saving API keys to the .env file."""
        if not n_clicks:
            return dash.no_update
            
        try:
            # Load current env file content
            env_path = Path(settings.BASE_DIR) / ".env"
            if not env_path.exists():
                return dbc.Alert([
                    html.I(className="fas fa-exclamation-circle me-2"),
                    "Error: .env file not found at the project root"
                ], color="danger", dismissable=True, className="mt-3")
                
            with open(env_path, "r") as f:
                env_content = f.read()
                
            # Update API keys if they're not masked
            if openai_key and not openai_key.startswith("•"):
                if "OPENAI_API_KEY=" in env_content:
                    env_content = re.sub(r"OPENAI_API_KEY=.*", f"OPENAI_API_KEY={openai_key}", env_content)
                else:
                    env_content += f"\nOPENAI_API_KEY={openai_key}"
                    
            if alchemy_key and not alchemy_key.startswith("•"):
                if "ALCHEMY_API_KEY=" in env_content:
                    env_content = re.sub(r"ALCHEMY_API_KEY=.*", f"ALCHEMY_API_KEY={alchemy_key}", env_content)
                else:
                    env_content += f"\nALCHEMY_API_KEY={alchemy_key}"
            
            if alchemy_solana_url and not alchemy_solana_url.startswith("•"):
                if "ALCHEMY_SOLANA_URL=" in env_content:
                    env_content = re.sub(r"ALCHEMY_SOLANA_URL=.*", f"ALCHEMY_SOLANA_URL={alchemy_solana_url}", env_content)
                else:
                    env_content += f"\nALCHEMY_SOLANA_URL={alchemy_solana_url}"
                    
            if langchain_key and not langchain_key.startswith("•"):
                if "LANGCHAIN_API_KEY=" in env_content:
                    env_content = re.sub(r"LANGCHAIN_API_KEY=.*", f"LANGCHAIN_API_KEY={langchain_key}", env_content)
                else:
                    env_content += f"\nLANGCHAIN_API_KEY={langchain_key}"
                
            # Write back to .env file
            with open(env_path, "w") as f:
                f.write(env_content)
                
            return dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                "API keys saved successfully"
            ], color="success", dismissable=True, className="mt-3")
            
        except Exception as e:
            return dbc.Alert([
                html.I(className="fas fa-exclamation-circle me-2"),
                f"Error saving API keys: {str(e)}"
            ], color="danger", dismissable=True, className="mt-3")

    @app.callback(
        Output("report-settings-save-status", "children"),
        Input("save-report-settings-button", "n_clicks"),
        prevent_initial_call=True
    )
    def handle_report_settings_save(n_clicks):
        """Handle saving report settings."""
        if n_clicks:
            return dbc.Alert([
                html.I(className="fas fa-check-circle me-2"),
                "Report settings would be saved here (demo only)"
            ], color="success", dismissable=True, className="mt-3")
        return dash.no_update
        
    # Toggle visibility callbacks for API key fields
    
    @app.callback(
        [Output("langchain-api-key", "type"),
         Output("toggle-langchain-visibility", "children")],
        Input("toggle-langchain-visibility", "n_clicks"),
        State("langchain-api-key", "type"),
        prevent_initial_call=True
    )
    def toggle_langchain_key_visibility(n_clicks, current_type):
        """Toggle visibility of LangChain API key."""
        if current_type == "password":
            return "text", html.I(className="fas fa-eye")
        return "password", html.I(className="fas fa-eye-slash")
    
    @app.callback(
        [Output("openai-api-key", "type"),
         Output("toggle-openai-visibility", "children")],
        Input("toggle-openai-visibility", "n_clicks"),
        State("openai-api-key", "type"),
        prevent_initial_call=True
    )
    def toggle_openai_key_visibility(n_clicks, current_type):
        """Toggle visibility of OpenAI API key."""
        if current_type == "password":
            return "text", html.I(className="fas fa-eye")
        return "password", html.I(className="fas fa-eye-slash")
    
    @app.callback(
        [Output("alchemy-api-key", "type"),
         Output("toggle-alchemy-visibility", "children")],
        Input("toggle-alchemy-visibility", "n_clicks"),
        State("alchemy-api-key", "type"),
        prevent_initial_call=True
    )
    def toggle_alchemy_key_visibility(n_clicks, current_type):
        """Toggle visibility of Alchemy API key."""
        if current_type == "password":
            return "text", html.I(className="fas fa-eye")
        return "password", html.I(className="fas fa-eye-slash")
    
    @app.callback(
        [Output("alchemy-solana-url", "type"),
         Output("toggle-alchemy-solana-visibility", "children")],
        Input("toggle-alchemy-solana-visibility", "n_clicks"),
        State("alchemy-solana-url", "type"),
        prevent_initial_call=True
    )
    def toggle_alchemy_solana_url_visibility(n_clicks, current_type):
        """Toggle visibility of Alchemy Solana URL."""
        if current_type == "password":
            return "text", html.I(className="fas fa-eye")
        return "password", html.I(className="fas fa-eye-slash")


def render_overview_page() -> List:
    """Render the overview page."""
    # Get sample data for demonstration
    assets = [
        {"name": "Bitcoin", "symbol": "BTC", "price": 65432.10, "change": 2.3, "volume": 28.5, "marketCap": 1.25},
        {"name": "Ethereum", "symbol": "ETH", "price": 3456.78, "change": -1.2, "volume": 12.3, "marketCap": 0.42},
        {"name": "Solana", "symbol": "SOL", "price": 123.45, "change": 5.6, "volume": 6.7, "marketCap": 0.05},
        {"name": "Cardano", "symbol": "ADA", "price": 0.48, "change": 0.8, "volume": 5.2, "marketCap": 0.02},
        {"name": "Polkadot", "symbol": "DOT", "price": 6.72, "change": -2.1, "volume": 3.1, "marketCap": 0.01},
    ]
    
    # Create a market overview chart
    df = pd.DataFrame(assets)
    
    # Better color scale for the bar chart
    colors = ['#FF5C5C' if c < 0 else '#5DFDCB' for c in df['change']]
    
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
    
    fig_price.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    # Create a market cap donut chart
    fig_market_cap = px.pie(
        df,
        values='marketCap',
        names='symbol',
        title='Market Cap Distribution (in Trillions USD)',
        hole=0.6,
        template="plotly_dark"
    )
    
    fig_market_cap.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif"),
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True
    )
    
    # Get the latest report snippet
    report = get_latest_report()
    report_preview = ""
    if report:
        content = report.get("content", "")
        # Just show the first few paragraphs
        paragraphs = content.split("\n\n")[:2]
        report_preview = "\n\n".join(paragraphs)
    
    return [
        dbc.Row([
            dbc.Col([
                html.H1("HiramAbiff Dashboard", className="mb-4 animate-on-scroll"),
                html.P("Chain-Agnostic DeFi Agent Dashboard with AI-Powered Market Analysis", className="lead animate-on-scroll"),
                html.Hr(),
            ], width=12)
        ]),
        
        dbc.Row([
            # Left column
            dbc.Col([
                # System Status Card
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-server me-2"),
                            "System Status"
                        ], className="d-flex align-items-center")
                    ]),
                    dbc.CardBody([
                        html.H4(className="status-active text-success", children="Active"),
                        html.P("All systems operational"),
                        html.P([
                            "Last updated: ",
                            html.Span(
                                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                className="live-timestamp"
                            )
                        ]),
                        
                        html.Div([
                            html.P("Services", className="mb-2 mt-3 fw-bold"),
                            dbc.Row([
                                dbc.Col(html.Span("Dashboard"), width=6),
                                dbc.Col(html.Span("✅ Online", className="text-success"), width=6),
                            ], className="mb-1"),
                            dbc.Row([
                                dbc.Col(html.Span("Market Analysis"), width=6),
                                dbc.Col(html.Span("✅ Online", className="text-success"), width=6),
                            ], className="mb-1"),
                            dbc.Row([
                                dbc.Col(html.Span("Wallet Services"), width=6),
                                dbc.Col(html.Span("✅ Online", className="text-success"), width=6),
                            ], className="mb-1"),
                        ])
                    ])
                ], className="mb-4 animate-on-scroll"),
                
                # Quick Actions Card
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-bolt me-2"),
                            "Quick Actions"
                        ], className="d-flex align-items-center")
                    ]),
                    dbc.CardBody([
                        dbc.Button([
                            html.I(className="fas fa-chart-line me-2"),
                            "Generate Market Report"
                        ], color="primary", className="mb-2 w-100", href="/dashboard/market-analysis"),
                        
                        dbc.Button([
                            html.I(className="fas fa-wallet me-2"),
                            "View Wallet Info"
                        ], color="secondary", className="mb-2 w-100", href="/dashboard/wallet-info"),
                        
                        dbc.Button([
                            html.I(className="fas fa-cog me-2"),
                            "Settings"
                        ], color="info", className="mb-2 w-100", href="/dashboard/settings"),
                        
                        dbc.Button([
                            html.I(className="fas fa-redo-alt me-2"),
                            "Update Data"
                        ], outline=True, color="light", className="w-100")
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
                            figure=fig_price,
                            responsive=True,
                            className="dash-graph mb-4"
                        ),
                        
                        html.Div([
                            html.H5("Top Performing Assets", className="mb-3"),
                            html.Div([
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
                                                html.Img(src=f"https://cryptologos.cc/logos/{asset['name'].lower()}-{asset['symbol'].lower()}-logo.png", 
                                                        height="20px", className="me-2",
                                                        style={"display": "inline"}),
                                                asset['symbol']
                                            ])
                                        ], width=2),
                                        dbc.Col([
                                            html.Div(f"${asset['price']:,.2f}", className="market-price")
                                        ], width=3),
                                        dbc.Col([
                                            html.Div(
                                                f"{asset['change']:+.2f}%", 
                                                className=f"{'price-change-positive' if asset['change'] >= 0 else 'price-change-negative'}"
                                            )
                                        ], width=3),
                                        dbc.Col([
                                            html.Div(f"${asset['volume']}B")
                                        ], width=2),
                                        dbc.Col([
                                            html.Div(f"${asset['marketCap']}T")
                                        ], width=2),
                                    ], className="mb-3 asset-row")
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
                        html.P(report_preview if report_preview else "No recent analysis available.", className="mb-3"),
                        dbc.Button([
                            html.I(className="fas fa-file-alt me-2"),
                            "View Full Report"
                        ], color="link", href="/dashboard/market-analysis"),
                    ])
                ], className="animate-on-scroll")
            ], width=12, lg=8),
        ]),
        
        # Bottom row - Statistics
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("System Statistics"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.H3("24", className="mb-0 animate-number", **{"data-target": "24", "data-duration": "2000"}),
                                    html.P("Hours Uptime", className="text-muted mb-0")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3("5", className="mb-0 animate-number", **{"data-target": "5", "data-duration": "2000"}),
                                    html.P("Reports Generated", className="text-muted mb-0")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3("2", className="mb-0 animate-number", **{"data-target": "2", "data-duration": "2000"}),
                                    html.P("Wallets Monitored", className="text-muted mb-0")
                                ], className="text-center")
                            ], width=3),
                            dbc.Col([
                                html.Div([
                                    html.H3("0", className="mb-0 animate-number", **{"data-target": "0", "data-duration": "2000"}),
                                    html.P("Active Trades", className="text-muted mb-0")
                                ], className="text-center")
                            ], width=3),
                        ])
                    ])
                ], className="mt-4 animate-number-container animate-on-scroll")
            ], width=12)
        ])
    ]


def render_market_analysis_page() -> List:
    """Render the market analysis page."""
    report = get_latest_report()
    
    return [
        dbc.Row([
            dbc.Col([
                html.H1([
                    html.I(className="fas fa-chart-line me-3"),
                    "AI Market Analysis"
                ], className="mb-4 animate-on-scroll"),
                html.P("AI-Generated Market Analysis and Projections for Trading Insights", className="lead animate-on-scroll"),
                html.Hr(),
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-robot me-2"),
                            "AI Report Generation",
                        ], className="d-flex align-items-center"),
                    ]),
                    dbc.CardBody([
                        html.P([
                            "Our AI analyzes multiple data sources including real-time market data, ",
                            "social sentiment, on-chain metrics, and historical patterns to generate ",
                            "comprehensive market reports with predictive insights."
                        ], className="mb-4"),
                        
                        dbc.Button(
                            [
                                html.I(className="fas fa-sync-alt me-2"),
                                "Generate New Report"
                            ],
                            id="generate-report-button", 
                            color="primary", 
                            className="mb-3"
                        ),
                        html.Div(id="report-generation-status"),
                    ])
                ], className="mb-4 animate-on-scroll")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Div(
                    render_report_content(report) if report else [
                        html.Div([
                            html.Div([
                                html.I(className="fas fa-file-alt fa-3x mb-3 text-muted"),
                                html.H4("No Reports Available", className="mb-3"),
                                html.P("Generate a new report to see market analysis and projections.", className="mb-4"),
                                dbc.Spinner(size="lg", color="primary", type="grow"),
                            ], className="text-center my-5")
                        ], className="animate-on-scroll")
                    ],
                    id="market-analysis-content"
                )
            ], width=12)
        ])
    ]


def render_wallet_info_page() -> List:
    """Render the wallet information page."""
    # Try to load deployment info
    deployment_info = {}
    try:
        deployment_path = Path("data/deployment_info.json")
        if deployment_path.exists():
            with open(deployment_path, "r") as f:
                deployment_info = json.load(f)
    except Exception as e:
        logger.error(f"Error loading deployment info: {e}")
    
    if not deployment_info:
        return [
            html.H1([
                html.I(className="fas fa-wallet me-3"),
                "Wallet Information"
            ], className="mb-4 animate-on-scroll"),
            html.P("No wallet information available.", className="lead animate-on-scroll"),
            dbc.Alert([
                html.I(className="fas fa-exclamation-triangle me-2"),
                "No deployment information found. Run the testnet launcher script first."
            ], color="warning", className="animate-on-scroll"),
            
            dbc.Card([
                dbc.CardHeader([
                    html.Div([
                        html.I(className="fas fa-terminal me-2"),
                        "Launch Instructions"
                    ], className="d-flex align-items-center")
                ]),
                dbc.CardBody([
                    html.P("To setup your wallet, run the testnet launcher script with the following command:"),
                    html.Div([
                        html.Code("python scripts/solana_testnet_launcher.py", className="bg-dark p-2 d-block rounded")
                    ], className="bg-dark p-3 rounded mb-3"),
                    html.P("This will create agent and trading wallets and request airdrops on the Solana testnet."),
                    dbc.Button([
                        html.I(className="fas fa-play me-2"),
                        "Run Launcher"
                    ], color="primary")
                ])
            ], className="mt-4 animate-on-scroll")
        ]
    
    # Create wallet cards
    agent_wallet = deployment_info.get("agent_wallet", "Not available")
    agent_balance = deployment_info.get("agent_balance", 0)
    trading_wallet = deployment_info.get("trading_wallet", "Not available")
    trading_balance = deployment_info.get("trading_balance", 0)
    network = deployment_info.get("network", "unknown")
    timestamp = deployment_info.get("timestamp", 0)
    
    deployed_date = datetime.datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") if timestamp else "Unknown"
    
    # Mock transaction history
    transactions = [
        {"type": "Airdrop", "amount": "1.0 SOL", "wallet": "Agent", "timestamp": datetime.datetime.now() - datetime.timedelta(hours=3), "status": "success"},
        {"type": "Airdrop", "amount": "1.0 SOL", "wallet": "Trading", "timestamp": datetime.datetime.now() - datetime.timedelta(hours=3), "status": "success"},
        {"type": "Transfer", "amount": "0.1 SOL", "wallet": "Agent → Trading", "timestamp": datetime.datetime.now() - datetime.timedelta(hours=2), "status": "success"},
        {"type": "Swap", "amount": "0.05 SOL → 1.2 USDC", "wallet": "Trading", "timestamp": datetime.datetime.now() - datetime.timedelta(hours=1), "status": "pending"},
    ]
    
    return [
        dbc.Row([
            dbc.Col([
                html.H1([
                    html.I(className="fas fa-wallet me-3"),
                    "Wallet Information"
                ], className="mb-4 animate-on-scroll"),
                html.P([
                    f"Wallet status on ",
                    html.Span(network, className="text-info text-capitalize"),
                    " network"
                ], className="lead animate-on-scroll"),
                html.Hr(),
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-server me-2"),
                            "Deployment Information"
                        ], className="d-flex align-items-center")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-network-wired fa-2x text-info"),
                                ], className="text-center")
                            ], width=2, className="d-flex align-items-center justify-content-center"),
                            dbc.Col([
                                html.Div([
                                    html.H5("Network", className="mb-1"),
                                    html.P(network.capitalize(), className="mb-0 text-info"),
                                ])
                            ], width=4),
                            dbc.Col([
                                html.Div([
                                    html.H5("Deployed", className="mb-1"),
                                    html.P(deployed_date, className="mb-0"),
                                ])
                            ], width=6),
                        ]),
                        html.Hr(),
                        html.Div([
                            html.P([
                                "The system is deployed on the Solana ",
                                html.Span(network, className="text-info"),
                                " network. This allows for testing and development in a safe environment before moving to mainnet."
                            ])
                        ])
                    ])
                ], className="mb-4 animate-on-scroll")
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-user-shield me-2"),
                            "Agent Wallet"
                        ], className="d-flex align-items-center justify-content-between"),
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-wallet fa-3x text-info mb-3"),
                                ], className="text-center")
                            ], width=12, md=3, className="d-flex align-items-center justify-content-center"),
                            dbc.Col([
                                html.H3([
                                    f"{agent_balance} ", 
                                    html.Span("SOL", className="text-muted fs-5")
                                ], className="text-info mb-3"),
                                html.P("Agent Wallet Address:"),
                                html.Div(agent_wallet, className="wallet-address text-truncate mb-3"),
                                html.Div([
                                    dbc.Button([
                                        html.I(className="fas fa-external-link-alt me-2"),
                                        "View on Explorer"
                                    ], 
                                    color="link", 
                                    href=f"https://explorer.solana.com/address/{agent_wallet}?cluster={network}",
                                    target="_blank",
                                    className="me-2"
                                    ),
                                    dbc.Button([
                                        html.I(className="fas fa-hand-holding-usd me-2"),
                                        "Request Airdrop"
                                    ], 
                                    color="outline-info", 
                                    size="sm"
                                    ),
                                ])
                            ], width=12, md=9),
                        ])
                    ])
                ], className="mb-4 animate-on-scroll")
            ], width=12, lg=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-chart-line me-2"),
                            "Trading Wallet"
                        ], className="d-flex align-items-center justify-content-between"),
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-exchange-alt fa-3x text-info mb-3"),
                                ], className="text-center")
                            ], width=12, md=3, className="d-flex align-items-center justify-content-center"),
                            dbc.Col([
                                html.H3([
                                    f"{trading_balance} ", 
                                    html.Span("SOL", className="text-muted fs-5")
                                ], className="text-info mb-3"),
                                html.P("Trading Wallet Address:"),
                                html.Div(trading_wallet, className="wallet-address text-truncate mb-3"),
                                html.Div([
                                    dbc.Button([
                                        html.I(className="fas fa-external-link-alt me-2"),
                                        "View on Explorer"
                                    ], 
                                    color="link", 
                                    href=f"https://explorer.solana.com/address/{trading_wallet}?cluster={network}",
                                    target="_blank",
                                    className="me-2"
                                    ),
                                    dbc.Button([
                                        html.I(className="fas fa-hand-holding-usd me-2"),
                                        "Request Airdrop"
                                    ], 
                                    color="outline-info", 
                                    size="sm"
                                    ),
                                ])
                            ], width=12, md=9),
                        ])
                    ])
                ], className="mb-4 animate-on-scroll")
            ], width=12, lg=6),
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-history me-2"),
                            "Recent Transactions",
                            dbc.Badge(f"{len(transactions)}", color="info", className="ms-2"),
                        ], className="d-flex align-items-center")
                    ]),
                    dbc.CardBody([
                        html.Div([
                            dbc.Row([
                                dbc.Col([
                                    html.Div("Type", className="fw-bold")
                                ], width=2),
                                dbc.Col([
                                    html.Div("Amount", className="fw-bold")
                                ], width=3),
                                dbc.Col([
                                    html.Div("Wallet", className="fw-bold")
                                ], width=3),
                                dbc.Col([
                                    html.Div("Time", className="fw-bold")
                                ], width=3),
                                dbc.Col([
                                    html.Div("Status", className="fw-bold")
                                ], width=1),
                            ], className="mb-2"),
                            
                            *[
                                dbc.Row([
                                    dbc.Col([
                                        html.Div(tx["type"])
                                    ], width=2),
                                    dbc.Col([
                                        html.Div(tx["amount"])
                                    ], width=3),
                                    dbc.Col([
                                        html.Div(tx["wallet"])
                                    ], width=3),
                                    dbc.Col([
                                        html.Div(tx["timestamp"].strftime("%H:%M:%S"))
                                    ], width=3),
                                    dbc.Col([
                                        html.Div(
                                            html.I(
                                                className=f"fas fa-{'check text-success' if tx['status'] == 'success' else 'clock text-warning'}"
                                            )
                                        )
                                    ], width=1),
                                ], className=f"mb-2 tx-row {'bg-light bg-opacity-10' if i % 2 == 0 else ''}")
                                for i, tx in enumerate(transactions)
                            ],
                            
                            html.Div([
                                dbc.Button([
                                    html.I(className="fas fa-list-ul me-2"),
                                    "View All Transactions"
                                ], color="link", className="mt-3")
                            ], className="text-center")
                        ])
                    ])
                ], className="mb-4 animate-on-scroll")
            ], width=12)
        ])
    ]


def render_settings_page() -> List:
    """Render the settings page."""
    return [
        dbc.Row([
            dbc.Col([
                html.H1([
                    html.I(className="fas fa-cog me-3"),
                    "Settings"
                ], className="mb-4 animate-on-scroll"),
                html.P("Configure your HiramAbiff instance settings and parameters", className="lead animate-on-scroll"),
                html.Hr(),
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-key me-2"),
                            "API Keys"
                        ], className="d-flex align-items-center")
                    ]),
                    dbc.CardBody([
                        html.P("Manage your API keys for various services. For security, API keys are stored in the .env file.", className="mb-4"),
                        
                        dbc.Row([
                            dbc.Label("LangChain API Key", html_for="langchain-api-key", width=4, className="text-end"),
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.Input(
                                        id="langchain-api-key",
                                        type="password",
                                        placeholder="Enter LangChain API Key",
                                        value="••••••••••••••••••••••••••••••••",
                                        className="border-end-0"
                                    ),
                                    dbc.InputGroupText(
                                        html.I(className="fas fa-eye-slash"),
                                        id="toggle-langchain-visibility",
                                        style={"cursor": "pointer"}
                                    ),
                                ]),
                                html.Small("Used for LangChain tracing and analyzing", className="text-muted d-block mt-1")
                            ], width=8),
                        ], className="mb-3 align-items-center"),
                        
                        dbc.Row([
                            dbc.Label("OpenAI API Key", html_for="openai-api-key", width=4, className="text-end"),
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.Input(
                                        id="openai-api-key",
                                        type="password",
                                        placeholder="Enter OpenAI API Key",
                                        value="••••••••••••••••••••••••••••••••",
                                        className="border-end-0"
                                    ),
                                    dbc.InputGroupText(
                                        html.I(className="fas fa-eye-slash"),
                                        id="toggle-openai-visibility",
                                        style={"cursor": "pointer"}
                                    ),
                                ]),
                                html.Small("Used for market analysis report generation", className="text-muted d-block mt-1")
                            ], width=8),
                        ], className="mb-3 align-items-center"),
                        
                        dbc.Row([
                            dbc.Label("Alchemy API Key", html_for="alchemy-api-key", width=4, className="text-end"),
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.Input(
                                        id="alchemy-api-key",
                                        type="password",
                                        placeholder="Enter Alchemy API Key",
                                        value="••••••••••••••••••••••••••••••••",
                                        className="border-end-0"
                                    ),
                                    dbc.InputGroupText(
                                        html.I(className="fas fa-eye-slash"),
                                        id="toggle-alchemy-visibility",
                                        style={"cursor": "pointer"}
                                    ),
                                ]),
                                html.Small("Used for blockchain data access", className="text-muted d-block mt-1")
                            ], width=8),
                        ], className="mb-3 align-items-center"),
                        
                        dbc.Row([
                            dbc.Label("Alchemy Solana URL", html_for="alchemy-solana-url", width=4, className="text-end"),
                            dbc.Col([
                                dbc.InputGroup([
                                    dbc.Input(
                                        id="alchemy-solana-url",
                                        type="password",
                                        placeholder="Enter Alchemy Solana URL",
                                        value="••••••••••••••••••••••••••••••••",
                                        className="border-end-0"
                                    ),
                                    dbc.InputGroupText(
                                        html.I(className="fas fa-eye-slash"),
                                        id="toggle-alchemy-solana-visibility",
                                        style={"cursor": "pointer"}
                                    ),
                                ]),
                                html.Small("Used for Solana blockchain operations", className="text-muted d-block mt-1")
                            ], width=8),
                        ], className="mb-3 align-items-center"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-save me-2"),
                                    "Save API Keys"
                                ], color="primary", id="save-api-keys-button", className="mt-3 float-end"),
                                html.Div(id="api-keys-save-status")
                            ], width=12),
                        ]),
                        
                        html.Hr(),
                        
                        html.Div([
                            html.P([
                                html.I(className="fas fa-info-circle me-2 text-info"),
                                "API keys are managed through the .env file for security. Changes made here will update your .env file."
                            ], className="mb-0 small text-muted")
                        ])
                    ])
                ], className="mb-4 animate-on-scroll")
            ], width=12, lg=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-file-alt me-2"),
                            "Report Settings"
                        ], className="d-flex align-items-center")
                    ]),
                    dbc.CardBody([
                        html.P("Configure how and when market analysis reports are generated.", className="mb-4"),
                        
                        dbc.Row([
                            dbc.Label("Report Generation Time", html_for="report-generation-time", width=4, className="text-end"),
                            dbc.Col([
                                dbc.Input(
                                    id="report-generation-time",
                                    type="time",
                                    value=settings.REPORT_GENERATION_TIME,
                                    className="border-end-0"
                                ),
                                html.Small("Time of day to generate daily reports (24-hour format)", className="text-muted d-block mt-1")
                            ], width=8),
                        ], className="mb-3 align-items-center"),
                        
                        dbc.Row([
                            dbc.Label("LLM Model", html_for="llm-model", width=4, className="text-end"),
                            dbc.Col([
                                dbc.Select(
                                    id="llm-model",
                                    options=[
                                        {"label": "GPT-4", "value": "gpt-4"},
                                        {"label": "GPT-4o", "value": "gpt-4o"},
                                        {"label": "GPT-3.5 Turbo", "value": "gpt-3.5-turbo"},
                                    ],
                                    value=settings.LLM_MODEL
                                ),
                                html.Small("AI model to use for analysis generation", className="text-muted d-block mt-1")
                            ], width=8),
                        ], className="mb-3 align-items-center"),
                        
                        dbc.Row([
                            dbc.Label([f"Temperature: ", html.Span(id="temperature-value", children=settings.LLM_TEMPERATURE)], html_for="llm-temperature", width=4, className="text-end"),
                            dbc.Col([
                                dcc.Slider(
                                    id="llm-temperature",
                                    min=0,
                                    max=1,
                                    step=0.1,
                                    value=settings.LLM_TEMPERATURE,
                                    marks={i/10: {"label": str(i/10), "style": {"transform": "rotate(45deg)", "white-space": "nowrap"}} for i in range(0, 11, 2)},
                                    className="mt-1"
                                ),
                                html.Small("Controls randomness - lower values are more deterministic", className="text-muted d-block mt-1")
                            ], width=8),
                        ], className="mb-3 align-items-center"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Button([
                                    html.I(className="fas fa-save me-2"),
                                    "Save Report Settings"
                                ], color="primary", id="save-report-settings-button", className="mt-3 float-end"),
                                html.Div(id="report-settings-save-status")
                            ], width=12),
                        ]),
                    ])
                ], className="mb-4 animate-on-scroll"),
                
                dbc.Card([
                    dbc.CardHeader([
                        html.Div([
                            html.I(className="fas fa-info-circle me-2"),
                            "System Information"
                        ], className="d-flex align-items-center")
                    ]),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col([
                                html.Div([
                                    html.I(className="fas fa-server fa-2x text-info")
                                ], className="text-center")
                            ], width=2, className="d-flex align-items-center justify-content-center"),
                            dbc.Col([
                                dbc.Row([
                                    dbc.Col([
                                        html.Div([
                                            html.Strong("Environment:", className="me-2"),
                                            html.Span(settings.APP_ENV, className="text-capitalize text-info")
                                        ], className="d-flex")
                                    ], width=6),
                                    dbc.Col([
                                        html.Div([
                                            html.Strong("Version:", className="me-2"),
                                            html.Span("0.1.0", className="text-info")
                                        ], className="d-flex")
                                    ], width=6),
                                ], className="mb-2"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Div([
                                            html.Strong("Debug Mode:", className="me-2"),
                                            html.Span("Enabled" if settings.APP_DEBUG else "Disabled", className="text-success" if settings.APP_DEBUG else "text-warning")
                                        ], className="d-flex")
                                    ], width=6),
                                    dbc.Col([
                                        html.Div([
                                            html.Strong("Host:", className="me-2"),
                                            html.Span(f"{settings.APP_HOST}:{settings.APP_PORT}", className="text-info")
                                        ], className="d-flex")
                                    ], width=6),
                                ])
                            ], width=10)
                        ], className="mb-3"),
                        html.Hr(),
                        html.Div([
                            dbc.Button([
                                html.I(className="fas fa-sync-alt me-2"),
                                "Restart Services",
                            ], color="outline-warning", size="sm", className="me-2"),
                            dbc.Button([
                                html.I(className="fas fa-file-alt me-2"),
                                "View Logs",
                            ], color="outline-info", size="sm"),
                        ], className="d-flex justify-content-end")
                    ])
                ], className="animate-on-scroll")
            ], width=12, lg=6),
        ]),
    ]


def render_report_content(report: Dict[str, Any]) -> List:
    """
    Render the content of a market analysis report.
    
    Args:
        report: The market analysis report
    
    Returns:
        List: HTML components to display the report
    """
    if not report:
        return [
            html.Div([
                html.H4("No report available"),
                html.P("Generate a new report to see market analysis."),
            ], className="text-center my-5")
        ]
    
    content = report.get("content", "")
    date = report.get("date", datetime.datetime.now().strftime("%Y-%m-%d"))
    generated_at = report.get("generated_at", "")
    
    # Format the generated_at time to be more readable
    try:
        dt = datetime.datetime.fromisoformat(generated_at)
        generated_at = dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        pass
    
    # Process the content into sections for better display
    sections = []
    current_section = {"title": "", "content": []}
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a section header
        if line.startswith('# '):
            if current_section["title"]:
                sections.append(current_section)
            current_section = {"title": line[2:], "content": []}
        elif line.startswith('## '):
            if current_section["title"]:
                sections.append(current_section)
            current_section = {"title": line[3:], "content": []}
        elif line.startswith('1.') or line.startswith('2.') or line.startswith('3.') or line.startswith('4.') or line.startswith('5.'):
            if current_section["title"]:
                sections.append(current_section)
            current_section = {"title": line, "content": []}
        else:
            current_section["content"].append(line)
    
    # Add the last section
    if current_section["title"]:
        sections.append(current_section)
    
    # If no sections were found, treat the whole content as one section
    if not sections:
        sections = [{"title": "Market Analysis", "content": content.split('\n')}]
    
    # Render the sections
    section_components = []
    for section in sections:
        section_components.append(html.H3(section["title"], className="mt-4"))
        
        for paragraph in section["content"]:
            if paragraph.startswith('-') or paragraph.startswith('*'):
                # It's a list item
                section_components.append(html.Li(paragraph[1:].strip()))
            else:
                # It's a regular paragraph
                section_components.append(html.P(paragraph))
    
    return [
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    f"Market Analysis Report - {date}",
                    html.Small(f"Generated: {generated_at}", className="text-muted")
                ], className="d-flex justify-content-between align-items-center"),
            ]),
            dbc.CardBody(section_components)
        ])
    ]


def get_latest_report() -> Optional[Dict[str, Any]]:
    """
    Get the latest market analysis report.
    
    Returns:
        Optional[Dict[str, Any]]: The latest report, or None if no reports exist.
    """
    try:
        return market_analysis_agent.get_latest_report()
    except Exception as e:
        logger.error(f"Error getting latest report: {e}")
        return None


def market_analysis_agent_mock():
    """
    Mock implementation of market_analysis_agent to avoid requiring LangChain.
    """
    class MockAgent:
        def get_latest_report(self):
            """Mock implementation that returns a sample report."""
            return {
                "content": """# Market Analysis Report

## Market Overview
The cryptocurrency market continues to show significant volatility with Bitcoin leading the way. Recent price action suggests a bullish trend in the short term, although some technical indicators are showing signs of potential correction.

## Key Observations
- Bitcoin has maintained support above the $60,000 level, suggesting strong buyer interest
- Ethereum's transition to Proof of Stake has reduced its environmental impact and potentially improved its tokenomics
- Layer 2 solutions are gaining traction as gas fees on Ethereum mainnet remain high
- DeFi protocols are showing signs of maturity with improved security measures

## Market Predictions
It appears likely that we'll see continued institutional adoption of cryptocurrencies in the coming months. Regulatory clarity in major markets could serve as a catalyst for the next leg up in prices.

## Investment Opportunities
Solana's ecosystem continues to grow despite recent technical challenges. Projects building on its infrastructure may present interesting investment opportunities due to lower fees and high throughput capabilities.""",
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "generated_at": datetime.datetime.now().isoformat()
            }
        
        async def generate_market_analysis(self):
            """Mock implementation that pretends to generate a report."""
            return "Generated mock report"

    return MockAgent()

# Use the mock agent instead of the real one when running in demo mode
market_analysis_agent = market_analysis_agent_mock() 