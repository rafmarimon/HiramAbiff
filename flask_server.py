#!/usr/bin/env python
"""
Minimal Flask server to test connectivity
"""

from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, Flask is working!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) 