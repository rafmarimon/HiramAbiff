#!/usr/bin/env python
"""
Minimal Dashboard for HiramAbiff
"""

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# Create a simple app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    title="HiramAbiff Minimal Dashboard",
    routes_pathname_prefix="/dashboard/"
)

# Create sample data
df = pd.DataFrame({
    "Asset": ["Bitcoin", "Ethereum", "Solana", "Cardano"],
    "Price": [65000, 3500, 125, 0.5],
    "Change": [2.5, -1.2, 5.6, 0.8]
})

# Create a simple bar chart
fig = px.bar(
    df, 
    x="Asset", 
    y="Price", 
    color="Change",
    labels={"Asset": "Cryptocurrency", "Price": "Price (USD)"},
    title="Asset Prices"
)

# Simple layout
app.layout = dbc.Container([
    html.H1("HiramAbiff Minimal Dashboard", className="my-4"),
    html.P("A simple dashboard demonstration"),
    
    dbc.Card([
        dbc.CardHeader("Asset Prices"),
        dbc.CardBody([
            dcc.Graph(figure=fig)
        ])
    ]),
    
    html.Footer("© 2025 HiramAbiff", className="mt-4 text-center text-muted")
], fluid=True)

# Run the server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8888, debug=True) 