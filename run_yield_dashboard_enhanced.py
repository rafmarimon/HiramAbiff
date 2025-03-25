#!/usr/bin/env python3
"""
HiramAbiff Yield Dashboard - Enhanced Version

This script runs an enhanced Flask-based dashboard for yield farming opportunities,
integrating wallet connection, portfolio management, and AI insights.
"""

import os
import json
import argparse
import logging
import datetime
import math
import random
from typing import Dict, List, Any, Optional

from flask import Flask, render_template, jsonify, request, redirect, url_for, session, send_from_directory

from src.blockchain.wallet_integration import wallet_integration
from src.yield_aggregator import YieldAggregator
from src.portfolio_manager import portfolio_manager
from src.yield_insights import YieldInsights

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
yield_aggregator = YieldAggregator()
yield_insights = YieldInsights()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'hiramabiff_secret_key')

# Session configuration
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7)

# Constants
DEFAULT_OPPORTUNITIES_LIMIT = 20

@app.route('/')
def index():
    """Render main dashboard page."""
    return render_template('dashboard/index.html', active_page='dashboard')

@app.route('/market')
def market():
    """Render market page."""
    return render_template('dashboard/market.html', active_page='market')

@app.route('/portfolio')
def portfolio():
    """Render portfolio page."""
    return render_template('dashboard/portfolio.html', active_page='portfolio')

@app.route('/staking')
def staking():
    """Render staking page."""
    return render_template('dashboard/staking.html', active_page='staking')

@app.route('/static/<path:filename>')
def serve_static(filename):
    """Serve static files."""
    return send_from_directory('static', filename)

# API routes

@app.route('/api/opportunities')
def get_opportunities():
    """Get yield opportunities."""
    try:
        # Parse query parameters
        limit = request.args.get('limit', DEFAULT_OPPORTUNITIES_LIMIT, type=int)
        min_tvl = request.args.get('min_tvl', 0, type=float)
        min_apy = request.args.get('min_apy', 0, type=float)
        max_risk = request.args.get('max_risk', 10, type=float)
        chain = request.args.get('chain')
        project = request.args.get('project')

        # Get data based on filters
        if chain:
            data = yield_aggregator.get_pools_by_chain(chain, min_tvl, min_apy, max_risk, limit)
        elif project:
            data = yield_aggregator.get_pools_by_project(project, min_tvl, min_apy, max_risk, limit)
        else:
            data = yield_aggregator.get_best_opportunities(min_tvl, min_apy, max_risk, limit)

        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting opportunities: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/market')
def get_market_data():
    """Get market data by chain or project."""
    try:
        chain = request.args.get('chain')
        project = request.args.get('project')
        
        # Get statistics based on filter
        if chain:
            stats_by_chain = yield_aggregator.get_stats_by_chain()
            if chain in stats_by_chain:
                return jsonify(stats_by_chain[chain])
            else:
                return jsonify({"error": f"Chain {chain} not found"}), 404
        elif project:
            stats_by_project = yield_aggregator.get_stats_by_project()
            if project in stats_by_project:
                return jsonify(stats_by_project[project])
            else:
                return jsonify({"error": f"Project {project} not found"}), 404
        else:
            # Return aggregated market data
            stats_by_chain = yield_aggregator.get_stats_by_chain()
            stats_by_project = yield_aggregator.get_stats_by_project()
            
            # Calculate totals
            total_tvl = sum(chain_data["total_tvl"] for chain_data in stats_by_chain.values())
            total_pools = sum(chain_data["count"] for chain_data in stats_by_chain.values())
            
            # Calculate weighted average APY
            weighted_apy = 0
            if total_tvl > 0:
                weighted_apy = sum(chain_data["avg_apy"] * chain_data["total_tvl"] / total_tvl 
                                  for chain_data in stats_by_chain.values())
            
            # Get top chains by TVL
            top_chains = sorted(stats_by_chain.items(), key=lambda x: x[1]["total_tvl"], reverse=True)[:5]
            top_chains = [{"chain": chain, "tvl": data["total_tvl"], "avg_apy": data["avg_apy"]} 
                         for chain, data in top_chains]
            
            # Get top projects by TVL
            top_projects = sorted(stats_by_project.items(), key=lambda x: x[1]["total_tvl"], reverse=True)[:5]
            top_projects = [{"project": project, "tvl": data["total_tvl"], "avg_apy": data["avg_apy"]} 
                           for project, data in top_projects]
            
            # Generate mock trends (in production this would be from historical data)
            tvl_trend = []
            apy_trend = []
            
            for i in range(30):
                date = (datetime.datetime.now() - datetime.timedelta(days=29-i)).strftime("%Y-%m-%d")
                
                # Simulate slightly increasing TVL trend
                tvl_factor = 0.95 + (i / 30) * 0.1
                daily_tvl = total_tvl * tvl_factor * random.uniform(0.98, 1.02)
                
                # Simulate slightly volatile APY trend
                apy_factor = 1 + 0.1 * math.sin(i / 5)
                daily_apy = weighted_apy * apy_factor * random.uniform(0.95, 1.05)
                
                tvl_trend.append({"date": date, "value": daily_tvl})
                apy_trend.append({"date": date, "value": daily_apy})
            
            return jsonify({
                "total_tvl": total_tvl,
                "total_pools": total_pools,
                "avg_apy": weighted_apy,
                "top_chains": top_chains,
                "top_projects": top_projects,
                "tvl_trend": tvl_trend,
                "apy_trend": apy_trend
            })
    except Exception as e:
        logger.error(f"Error getting market data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/add-strategy', methods=['POST'])
def add_strategy():
    """Add a strategy to the active portfolio."""
    try:
        data = request.json
        opportunity_id = data.get('opportunity_id')
        invested_amount = data.get('invested_amount')
        duration = data.get('duration', 365)
        compound_frequency = data.get('compound_frequency', 'daily')
        
        if not opportunity_id or not invested_amount:
            return jsonify({"error": "Missing required parameters"}), 400
        
        result = portfolio_manager.add_strategy(opportunity_id, invested_amount, duration, compound_frequency)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error adding strategy: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/remove-strategy', methods=['POST'])
def remove_strategy():
    """Remove a strategy from the active portfolio."""
    try:
        data = request.json
        strategy_id = data.get('strategy_id')
        
        if not strategy_id:
            return jsonify({"error": "Missing strategy_id parameter"}), 400
        
        result = portfolio_manager.remove_strategy(strategy_id)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error removing strategy: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio')
def get_portfolio():
    """Get the active portfolio."""
    try:
        portfolio = portfolio_manager.get_active_portfolio()
        return jsonify(portfolio)
    except Exception as e:
        logger.error(f"Error getting portfolio: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/performance')
def get_portfolio_performance():
    """Get portfolio performance data."""
    try:
        period = request.args.get('period', '1y')
        
        # Default to 1 year (365 days)
        days = 365
        
        if period == '1d':
            days = 1
        elif period == '1w':
            days = 7
        elif period == '1m':
            days = 30
        elif period == '3m':
            days = 90
        elif period == '6m':
            days = 180
        elif period == 'all':
            days = 730  # 2 years
        
        simulation = portfolio_manager.simulate_portfolio_returns(days)
        
        if "error" in simulation:
            return jsonify(simulation), 400
        
        # Extract projection data
        data = []
        for point in simulation.get("projection", []):
            # Calculate date based on days
            date = (datetime.datetime.now() - datetime.timedelta(days=days) + 
                   datetime.timedelta(days=point["days"])).strftime("%Y-%m-%d")
            
            data.append({
                "date": date,
                "value": point["value"]
            })
        
        return jsonify({
            "initial_value": simulation.get("initial_value", 0),
            "final_value": simulation.get("final_value", 0),
            "total_growth": simulation.get("total_growth", 0),
            "total_growth_pct": simulation.get("total_growth_pct", 0),
            "avg_apy": simulation.get("current_apy_weighted", 0),
            "data": data
        })
    except Exception as e:
        logger.error(f"Error getting portfolio performance: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/optimization')
def get_portfolio_optimization():
    """Get portfolio optimization suggestions."""
    try:
        suggestions = portfolio_manager.create_optimization_suggestion()
        
        if "error" in suggestions:
            return jsonify(suggestions), 400
        
        return jsonify(suggestions)
    except Exception as e:
        logger.error(f"Error getting optimization suggestions: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/portfolio/risk')
def get_portfolio_risk():
    """Get portfolio risk metrics."""
    try:
        risk_metrics = portfolio_manager.calculate_portfolio_risk()
        
        if "error" in risk_metrics:
            return jsonify(risk_metrics), 400
        
        return jsonify(risk_metrics)
    except Exception as e:
        logger.error(f"Error getting portfolio risk metrics: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard')
def get_dashboard_data():
    """Get main dashboard data."""
    try:
        # Get portfolio data
        portfolio = portfolio_manager.get_active_portfolio()
        
        # Get wallet data
        wallet_data = wallet_integration.get_wallet_data()
        wallet_connected = "error" not in wallet_data
        
        # Get risk metrics
        risk_metrics = portfolio_manager.calculate_portfolio_risk()
        
        # Calculate number of active chains
        active_chains = set()
        for strategy in portfolio.get("strategies", []):
            chain = strategy.get("chain")
            if chain:
                active_chains.add(chain)
        
        # Mock data for total value change and APY change
        total_value_change = random.uniform(-5, 15)
        avg_apy_change = random.uniform(-2, 5)
        
        # Format wallet data
        wallet_balance = 0
        wallet_staked = 0
        wallet_yield = 0
        wallet_yield_pct = 0
        wallet_tokens = []
        
        if wallet_connected:
            wallet_tokens = wallet_data.get("tokens", [])
            wallet_balance = sum(token.get("value_usd", 0) for token in wallet_tokens)
            
            staked_assets = wallet_data.get("staked", [])
            wallet_staked = sum(asset.get("value_usd", 0) for asset in staked_assets)
            
            wallet_yield = sum(asset.get("value_usd", 0) * asset.get("apy", 0) / 100 for asset in staked_assets)
            wallet_yield_pct = wallet_yield / wallet_balance * 100 if wallet_balance > 0 else 0
        
        return jsonify({
            "total_value": portfolio.get("total_current_value", 0),
            "total_value_change": total_value_change,
            "avg_apy": risk_metrics.get("avg_risk_score", 0) if "avg_risk_score" in risk_metrics else 0,
            "avg_apy_change": avg_apy_change,
            "active_strategies": len(portfolio.get("strategies", [])),
            "active_chains": len(active_chains),
            "risk_level": risk_metrics.get("risk_level", "Medium") if "risk_level" in risk_metrics else "Medium",
            "risk_score": risk_metrics.get("avg_risk_score", 5) if "avg_risk_score" in risk_metrics else 5,
            "wallet_connected": wallet_connected,
            "wallet_balance": wallet_balance,
            "wallet_staked": wallet_staked,
            "wallet_yield": wallet_yield,
            "wallet_yield_pct": wallet_yield_pct,
            "wallet_tokens": wallet_tokens
        })
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate-insights')
def generate_insights():
    """Generate AI insights about market and portfolio."""
    try:
        # Get yield data
        yield_data = yield_aggregator.get_data()
        
        # Get portfolio data
        portfolio = portfolio_manager.get_active_portfolio()
        
        # Generate insights
        insights = []
        
        # Market trend insight
        market_trend = yield_insights.analyze_market_trends(yield_data)
        insights.append({
            "type": "trend",
            "title": "Market Trend",
            "content": market_trend
        })
        
        # Top opportunity insight
        top_opportunity = yield_insights.find_top_opportunities(yield_data)
        insights.append({
            "type": "opportunity",
            "title": "Top Opportunity",
            "content": top_opportunity
        })
        
        # Portfolio insight
        if portfolio.get("strategies"):
            portfolio_insight = yield_insights.analyze_portfolio(portfolio)
            insights.append({
                "type": "portfolio",
                "title": "Portfolio Analysis",
                "content": portfolio_insight
            })
        
        # Risk warning insight
        risk_warning = yield_insights.identify_risks(yield_data, portfolio)
        if risk_warning:
            insights.append({
                "type": "warning",
                "title": "Risk Warning",
                "content": risk_warning
            })
        
        # Generate summary
        summary = yield_insights.generate_summary(insights)
        
        return jsonify({
            "insights": insights,
            "summary": summary
        })
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/connect-wallet', methods=['POST'])
def connect_wallet():
    """Connect to a wallet."""
    try:
        data = request.json
        wallet_type = data.get('wallet_type')
        
        if not wallet_type:
            return jsonify({"error": "Missing wallet_type parameter"}), 400
        
        success, message = wallet_integration.connect_wallet(wallet_type)
        
        if success:
            return jsonify({
                "success": True,
                "message": message,
                "wallet_address": wallet_integration.wallet_address,
                "wallet_type": wallet_integration.wallet_type
            })
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        logger.error(f"Error connecting wallet: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/wallet/disconnect', methods=['POST'])
def disconnect_wallet():
    """Disconnect the wallet."""
    try:
        success, message = wallet_integration.disconnect_wallet()
        
        if success:
            return jsonify({"success": True, "message": message})
        else:
            return jsonify({"success": False, "error": message}), 400
    except Exception as e:
        logger.error(f"Error disconnecting wallet: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/wallet/status')
def wallet_status():
    """Get wallet connection status."""
    try:
        return jsonify({
            "connected": wallet_integration.connected,
            "address": wallet_integration.wallet_address,
            "wallet_type": wallet_integration.wallet_type
        })
    except Exception as e:
        logger.error(f"Error getting wallet status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet/data')
def wallet_data():
    """Get wallet data."""
    try:
        data = wallet_integration.get_wallet_data()
        return jsonify(data)
    except Exception as e:
        logger.error(f"Error getting wallet data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet/stake-hiram', methods=['POST'])
def stake_hiram():
    """Stake HIRAM tokens."""
    try:
        data = request.json
        amount = data.get('amount')
        
        if amount is None:
            return jsonify({"error": "Missing amount parameter"}), 400
        
        result = wallet_integration.stake_hiram(float(amount))
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error staking HIRAM: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet/unstake-hiram', methods=['POST'])
def unstake_hiram():
    """Unstake HIRAM tokens."""
    try:
        data = request.json
        amount = data.get('amount')
        
        if amount is None:
            return jsonify({"error": "Missing amount parameter"}), 400
        
        result = wallet_integration.unstake_hiram(float(amount))
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error unstaking HIRAM: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet/staking-info')
def staking_info():
    """Get HIRAM staking information."""
    try:
        result = wallet_integration.get_staking_info()
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting staking info: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/wallet/fee-history')
def fee_history():
    """Get fee history."""
    try:
        result = wallet_integration.get_fee_history()
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting fee history: {e}")
        return jsonify({"error": str(e)}), 500

def main():
    """Run the application."""
    parser = argparse.ArgumentParser(description='Run the yield dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Host to run the app on')
    parser.add_argument('--port', type=int, default=8889, help='Port to run the app on')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    parser.add_argument('--demo', action='store_true', help='Run with demo data')
    
    args = parser.parse_args()
    
    if args.demo:
        logger.info("Running in demo mode with mock data")
        # Set components to use mock data
    
    logger.info(f"Starting yield dashboard on {args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=args.debug)

if __name__ == '__main__':
    main() 