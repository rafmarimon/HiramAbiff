#!/usr/bin/env python
"""
Minimal Dash app to test if Dash is working correctly
"""

import dash
from dash import html

# Create a simple Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Hello, Dash!"),
    html.P("This is a minimal Dash app to test if Dash is working correctly."),
])

# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True) 