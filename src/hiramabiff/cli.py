#!/usr/bin/env python
"""
HiramAbiff Command Line Interface

This module provides a command-line interface for the HiramAbiff package,
allowing users to run various DeFi agents and tools.
"""

import asyncio
import argparse
import sys
import os
import json
import pandas as pd
from datetime import datetime
from typing import List, Optional, Dict, Any

from loguru import logger

# Add the src directory to the Python path if running directly
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, "../.."))
if os.path.basename(src_dir) == "src":
    sys.path.insert(0, os.path.dirname(src_dir))

try:
    from hiramabiff import __version__
    from hiramabiff.agents import MinimalDeFiAgent
    from hiramabiff.wallet import WalletManager
    from hiramabiff.analysis import TokenTracker, LLMAnalyzer, TokenVisualizer
except ImportError:
    # If we're running the script directly, we need to modify the import paths
    import importlib.util
    
    # Import MinimalDeFiAgent
    minimal_agent_spec = importlib.util.spec_from_file_location(
        "minimal_defi_agent", 
        os.path.join(current_dir, "agents/minimal_defi_agent.py")
    )
    minimal_defi_agent = importlib.util.module_from_spec(minimal_agent_spec)
    minimal_agent_spec.loader.exec_module(minimal_defi_agent)
    MinimalDeFiAgent = minimal_defi_agent.MinimalDeFiAgent
    
    # Import WalletManager
    wallet_spec = importlib.util.spec_from_file_location(
        "wallet_manager",
        os.path.join(current_dir, "wallet/wallet_manager.py")
    )
    wallet_module = importlib.util.module_from_spec(wallet_spec)
    wallet_spec.loader.exec_module(wallet_module)
    WalletManager = wallet_module.WalletManager
    
    # Import TokenTracker
    token_spec = importlib.util.spec_from_file_location(
        "token_tracker",
        os.path.join(current_dir, "analysis/token_tracker.py")
    )
    token_module = importlib.util.module_from_spec(token_spec)
    token_spec.loader.exec_module(token_module)
    TokenTracker = token_module.TokenTracker
    
    # Import LLMAnalyzer
    llm_spec = importlib.util.spec_from_file_location(
        "llm_analyzer",
        os.path.join(current_dir, "analysis/llm_analyzer.py")
    )
    llm_module = importlib.util.module_from_spec(llm_spec)
    llm_spec.loader.exec_module(llm_module)
    LLMAnalyzer = llm_module.LLMAnalyzer
    
    # Import TokenVisualizer
    visualizer_spec = importlib.util.spec_from_file_location(
        "token_visualizer",
        os.path.join(current_dir, "analysis/visualizer.py")
    )
    visualizer_module = importlib.util.module_from_spec(visualizer_spec)
    visualizer_spec.loader.exec_module(visualizer_module)
    TokenVisualizer = visualizer_module.TokenVisualizer
    
    __version__ = "0.1.0"  # Default version if not installed


def setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI application.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    log_level = "DEBUG" if verbose else "INFO"
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Remove default logger
    logger.remove()
    
    # Add stderr logger with appropriate level
    logger.add(sys.stderr, format=log_format, level=log_level)
    
    # Add file logger
    logger.add(
        "hiramabiff_{time}.log",
        rotation="10 MB", 
        retention="1 week",
        format=log_format,
        level="DEBUG",
    )


async def run_yield_finder(
    chains: List[str],
    min_yield: float = 5.0,
    min_tvl: float = 500000.0,
    max_results: int = 5,
    agent_name: str = "YieldHunter",
) -> None:
    """Run the yield finder agent.
    
    Args:
        chains: List of blockchain names to analyze
        min_yield: Minimum yield percentage to include
        min_tvl: Minimum TVL (Total Value Locked) to include
        max_results: Maximum number of results to display
        agent_name: Name to give the agent
    """
    logger.info(f"Starting yield finder with chains: {chains}")
    
    # Create the agent
    agent = MinimalDeFiAgent(
        name=agent_name,
        min_yield_threshold=min_yield,
        min_tvl_threshold=min_tvl,
        max_opportunities=max_results,
    )
    
    # Run the agent
    results = await agent.run(chains=chains)
    
    if results:
        agent.print_report(results)
    else:
        logger.warning("No yield opportunities found matching the criteria")


async def run_wallet_command(args) -> None:
    """Run wallet-related commands.
    
    Args:
        args: Command line arguments
    """
    wallet_manager = WalletManager()
    
    if args.wallet_command == "create":
        try:
            wallet_info = wallet_manager.create_wallet(args.chain, args.name)
            print(f"\n✅ Wallet created successfully!")
            print(f"Name: {wallet_info['name']}")
            print(f"Chain: {wallet_info['chain']}")
            
            if args.chain.lower() == "solana":
                print(f"Public Key: {wallet_info['public_key']}")
                print(f"Private Key (keep secure!): {wallet_info['private_key_b58']}")
            elif args.chain.lower() == "ethereum":
                print(f"Address: {wallet_info['address']}")
                print(f"Private Key (keep secure!): {wallet_info['private_key']}")
                
            print(f"\nWallet stored at: {os.path.join(wallet_manager.wallet_dir, f'{args.name}.json')}")
                
        except ValueError as e:
            logger.error(f"Error creating wallet: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            
    elif args.wallet_command == "import":
        if not args.private_key:
            logger.error("Private key is required for import")
            print("\n❌ Error: Private key is required for import")
            return
            
        try:
            wallet_info = wallet_manager.import_wallet(args.chain, args.name, args.private_key)
            print(f"\n✅ Wallet imported successfully!")
            print(f"Name: {wallet_info['name']}")
            print(f"Chain: {wallet_info['chain']}")
            
            if args.chain.lower() == "solana":
                print(f"Public Key: {wallet_info['public_key']}")
            elif args.chain.lower() == "ethereum":
                print(f"Address: {wallet_info['address']}")
                
            print(f"\nWallet stored at: {os.path.join(wallet_manager.wallet_dir, f'{args.name}.json')}")
                
        except ValueError as e:
            logger.error(f"Error importing wallet: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            
    elif args.wallet_command == "list":
        wallets = wallet_manager.list_wallets()
        
        if not wallets:
            print("\nNo wallets found.")
            return
            
        print("\n📋 Wallet List")
        print("======================")
        
        for wallet in wallets:
            print(f"Name: {wallet['name']}")
            print(f"Chain: {wallet['chain']}")
            
            if wallet['chain'].lower() == "solana":
                print(f"Public Key: {wallet.get('public_key', 'N/A')}")
            elif wallet['chain'].lower() == "ethereum":
                print(f"Address: {wallet.get('address', 'N/A')}")
                
            print("----------------------")
            
    elif args.wallet_command == "balance":
        if not args.name:
            logger.error("Wallet name is required for balance check")
            print("\n❌ Error: Wallet name is required for balance check")
            return
            
        try:
            balance_info = await wallet_manager.get_balance(args.name)
            
            print(f"\n💰 Wallet Balance")
            print("======================")
            print(f"Wallet: {balance_info['wallet']}")
            print(f"Chain: {balance_info['chain']}")
            
            if balance_info['chain'].lower() == "solana":
                print(f"Address: {balance_info['address']}")
                print(f"Balance: {balance_info['balance']['sol']} SOL ({balance_info['balance']['lamports']} lamports)")
            elif balance_info['chain'].lower() == "ethereum":
                print(f"Address: {balance_info['address']}")
                print(f"Balance: {balance_info['balance']['eth']} ETH ({balance_info['balance']['wei']} wei)")
                
        except ValueError as e:
            logger.error(f"Error getting wallet balance: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            
    elif args.wallet_command == "delete":
        if not args.name:
            logger.error("Wallet name is required for deletion")
            print("\n❌ Error: Wallet name is required for deletion")
            return
            
        try:
            result = wallet_manager.delete_wallet(args.name)
            
            if result:
                print(f"\n✅ Wallet '{args.name}' deleted successfully.")
            else:
                print(f"\n❌ Wallet '{args.name}' not found.")
                
        except Exception as e:
            logger.error(f"Error deleting wallet: {str(e)}")
            print(f"\n❌ Error: {str(e)}")


async def run_token_command(args) -> None:
    """Run token-related commands.
    
    Args:
        args: Command line arguments
    """
    token_tracker = TokenTracker()
    
    if args.token_command == "price":
        try:
            price_data = await token_tracker.get_token_price(args.symbol)
            
            print(f"\n💹 {price_data['symbol']} Price")
            print("======================")
            print(f"Price: ${price_data['price_usd']:.4f}")
            print(f"Market Cap: ${price_data['market_cap_usd']:,.2f}")
            print(f"24h Volume: ${price_data['volume_24h_usd']:,.2f}")
            print(f"24h Change: {price_data['change_24h_percent']:.2f}%")
            print(f"Last Updated: {price_data['last_updated']}")
            
        except ValueError as e:
            logger.error(f"Error getting token price: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            
    elif args.token_command == "analyze":
        try:
            print(f"\nAnalyzing {args.symbol}...")
            analysis_data = await token_tracker.analyze_token(args.symbol)
            
            print(f"\n📊 {analysis_data['symbol']} Analysis")
            print("======================")
            print(f"Current Price: ${analysis_data['current_price_usd']:.4f}")
            print(f"Market Cap: ${analysis_data['market_cap_usd']:,.2f}")
            print(f"24h Change: {analysis_data['change_24h_percent']:.2f}%")
            print(f"7d Change: {analysis_data['change_7d_percent']:.2f}%")
            print("\n30-Day Statistics:")
            print(f"- Average Price: ${analysis_data['stats']['mean_price_30d']:.4f}")
            print(f"- Min Price: ${analysis_data['stats']['min_price_30d']:.4f}")
            print(f"- Max Price: ${analysis_data['stats']['max_price_30d']:.4f}")
            print(f"- Volatility: {analysis_data['stats']['volatility_30d']:.4f}")
            print(f"\nAnalysis Date: {analysis_data['analysis_date']}")
            
            # Generate chart if requested
            if args.chart:
                print("\nGenerating price chart...")
                visualizer = TokenVisualizer()
                
                # Get historical data
                historical_data = await token_tracker.get_token_historical_data(args.symbol, days=args.days)
                
                # Convert to pandas DataFrame
                df = pd.DataFrame(historical_data["price_data"])
                
                # Create chart
                chart_path = visualizer.create_price_chart(
                    df, 
                    args.symbol,
                    days=args.days,
                    show_volume=True,
                    show_ma=True,
                    ma_periods=[7, 30],
                    save=True,
                    show=args.show
                )
                
                print(f"\n✅ Chart saved to: {chart_path}")
            
            # If --llm flag is set, use LLM to analyze the token
            if args.llm:
                print("\nGenerating LLM analysis (this may take a moment)...")
                llm_analyzer = LLMAnalyzer()
                llm_result = await llm_analyzer.analyze_token_data(analysis_data)
                
                print("\n🤖 LLM Analysis")
                print("======================")
                print(llm_result["llm_analysis"]["text"])
                print(f"\nGenerated using {llm_result['llm_analysis']['model']} at {llm_result['llm_analysis']['generated_at']}")
            
        except ValueError as e:
            logger.error(f"Error analyzing token: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            
    elif args.token_command == "portfolio":
        try:
            # Parse the wallet addresses from the input
            wallets = {}
            for wallet_str in args.wallets:
                try:
                    chain, address = wallet_str.split(":")
                    wallets[chain] = address
                except ValueError:
                    logger.error(f"Invalid wallet format: {wallet_str}. Use 'chain:address'")
                    print(f"\n❌ Error: Invalid wallet format: {wallet_str}. Use 'chain:address'")
                    return
            
            print(f"\nAnalyzing portfolio across {len(wallets)} wallets...")
            portfolio_data = await token_tracker.generate_portfolio_analysis(wallets)
            
            print(f"\n📈 Portfolio Analysis")
            print("======================")
            print(f"Total Value: ${portfolio_data['total_value_usd']:,.2f}")
            
            print("\nToken Distribution:")
            for token, info in portfolio_data.get('token_distribution', {}).items():
                print(f"- {token}: {info.get('percentage', 0):.2f}% (${info.get('value_usd', 0):,.2f})")
                
            print(f"\nGenerated at: {portfolio_data['generated_at']}")
            
            # Generate pie chart if requested
            if args.chart:
                print("\nGenerating portfolio distribution chart...")
                visualizer = TokenVisualizer()
                
                chart_path = visualizer.create_portfolio_pie_chart(
                    portfolio_data,
                    title=f"Portfolio Distribution - {datetime.now().strftime('%Y-%m-%d')}",
                    min_pct=2.0,
                    save=True,
                    show=args.show
                )
                
                print(f"\n✅ Chart saved to: {chart_path}")
            
            # If --llm flag is set, use LLM to generate a portfolio report
            if args.llm:
                print("\nGenerating LLM portfolio report (this may take a moment)...")
                
                # Get market overview for context
                try:
                    btc_price = await token_tracker.get_token_price("bitcoin")
                    eth_price = await token_tracker.get_token_price("ethereum")
                    
                    market_overview = {
                        "btc_price": btc_price["price_usd"],
                        "eth_price": eth_price["price_usd"],
                        "market_trend": "Bullish" if btc_price["change_24h_percent"] > 0 else "Bearish",
                    }
                except Exception as e:
                    logger.warning(f"Could not get market overview: {str(e)}")
                    market_overview = None
                
                llm_analyzer = LLMAnalyzer()
                report = await llm_analyzer.generate_portfolio_report(portfolio_data, market_overview)
                
                print("\n🤖 LLM Portfolio Report")
                print("======================")
                print(report["llm_report"]["text"])
                print(f"\nGenerated using {report['llm_report']['model']} at {report['llm_report']['generated_at']}")
            
        except ValueError as e:
            logger.error(f"Error analyzing portfolio: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            
    elif args.token_command == "compare":
        try:
            visualizer = TokenVisualizer()
            
            print(f"\nComparing tokens: {', '.join(args.symbols)}...")
            
            # Get historical data for each token
            data_frames = {}
            for symbol in args.symbols:
                print(f"Fetching data for {symbol}...")
                historical_data = await token_tracker.get_token_historical_data(symbol, days=args.days)
                df = pd.DataFrame(historical_data["price_data"])
                data_frames[symbol] = df
            
            # Create comparison chart
            print("Generating comparison chart...")
            chart_path = visualizer.create_multi_token_chart(
                data_frames,
                days=args.days,
                normalized=args.normalized,
                save=True,
                show=args.show
            )
            
            print(f"\n✅ Chart saved to: {chart_path}")
            
            # Generate correlation heatmap if requested
            if args.correlation:
                print("Generating correlation heatmap...")
                corr_path = visualizer.create_price_correlation_heatmap(
                    data_frames,
                    days=args.days,
                    save=True,
                    show=args.show
                )
                
                print(f"\n✅ Correlation heatmap saved to: {corr_path}")
            
        except ValueError as e:
            logger.error(f"Error comparing tokens: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            
    elif args.token_command == "volatility":
        try:
            visualizer = TokenVisualizer()
            
            print(f"\nAnalyzing volatility for: {', '.join(args.symbols)}...")
            
            # Get and analyze each token
            token_analyses = {}
            for symbol in args.symbols:
                print(f"Analyzing {symbol}...")
                analysis_data = await token_tracker.analyze_token(symbol)
                token_analyses[symbol] = analysis_data
            
            # Create volatility comparison chart
            print("Generating volatility comparison chart...")
            chart_path = visualizer.create_volatility_comparison(
                token_analyses,
                save=True,
                show=args.show
            )
            
            print(f"\n✅ Chart saved to: {chart_path}")
            
        except ValueError as e:
            logger.error(f"Error analyzing volatility: {str(e)}")
            print(f"\n❌ Error: {str(e)}")


async def run_llm_command(args) -> None:
    """Run LLM-related commands.
    
    Args:
        args: Command line arguments
    """
    llm_analyzer = LLMAnalyzer()
    
    if args.llm_command == "market":
        try:
            print("\nGenerating market analysis (this may take a moment)...")
            market_analysis = await llm_analyzer.analyze_market_trend()
            
            print("\n🌍 Market Analysis")
            print("======================")
            print(market_analysis["llm_analysis"]["text"])
            print(f"\nGenerated using {market_analysis['llm_analysis']['model']} at {market_analysis['llm_analysis']['generated_at']}")
            
            # If output file is specified, save markdown version to file
            if args.output:
                output_path = args.output
                if not output_path.endswith(".md"):
                    output_path += ".md"
                    
                with open(output_path, "w") as f:
                    f.write("# Cryptocurrency Market Analysis\n\n")
                    f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(market_analysis["llm_analysis"]["text"])
                    f.write(f"\n\n---\n*Generated by HiramAbiff v{__version__} using {market_analysis['llm_analysis']['model']}*")
                    
                print(f"\nAnalysis saved to {output_path}")
                
        except ValueError as e:
            logger.error(f"Error generating market analysis: {str(e)}")
            print(f"\n❌ Error: {str(e)}")
            
    elif args.llm_command == "strategy":
        try:
            # First, get yield opportunities using the MinimalDeFiAgent
            print("\nFetching DeFi opportunities...")
            
            agent = MinimalDeFiAgent(
                name="StrategyAdvisor",
                min_yield_threshold=args.min_yield,
                min_tvl_threshold=args.min_tvl,
                max_opportunities=args.max_opportunities,
            )
            
            opportunities = await agent.run(chains=args.chains)
            
            if not opportunities:
                print("\n❌ No opportunities found matching the criteria.")
                return
                
            print(f"\nFound {len(opportunities)} opportunities matching the criteria.")
            print("\nGenerating investment strategy (this may take a moment)...")
            
            strategy = await llm_analyzer.generate_defi_strategy(
                opportunities,
                risk_profile=args.risk_profile,
                investment_amount=args.amount,
            )
            
            print("\n💼 DeFi Investment Strategy")
            print("======================")
            print(strategy["llm_strategy"]["text"])
            print(f"\nGenerated using {strategy['llm_strategy']['model']} at {strategy['llm_strategy']['generated_at']}")
            
            # If output file is specified, save markdown version to file
            if args.output:
                output_path = args.output
                if not output_path.endswith(".md"):
                    output_path += ".md"
                    
                with open(output_path, "w") as f:
                    f.write(f"# DeFi Investment Strategy ({args.risk_profile.title()} Risk)\n\n")
                    f.write(f"Investment Amount: ${args.amount:,.2f}\n\n")
                    f.write(f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(strategy["llm_strategy"]["text"])
                    f.write(f"\n\n---\n*Generated by HiramAbiff v{__version__} using {strategy['llm_strategy']['model']}*")
                    
                print(f"\nStrategy saved to {output_path}")
                
        except ValueError as e:
            logger.error(f"Error generating investment strategy: {str(e)}")
            print(f"\n❌ Error: {str(e)}")


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description=f"HiramAbiff DeFi Agent CLI v{__version__}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    
    parser.add_argument(
        "--version", "-v", 
        action="version", 
        version=f"HiramAbiff v{__version__}"
    )
    
    parser.add_argument(
        "--verbose", 
        action="store_true", 
        help="Enable verbose logging"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Yield finder command
    yield_parser = subparsers.add_parser(
        "yield", 
        help="Find the best yield opportunities"
    )
    
    yield_parser.add_argument(
        "--chains", "-c",
        nargs="+",
        default=["Solana", "Ethereum"],
        help="Chains to analyze (e.g., Solana Ethereum)",
    )
    
    yield_parser.add_argument(
        "--min-yield", "-y",
        type=float,
        default=5.0,
        help="Minimum yield percentage to include",
    )
    
    yield_parser.add_argument(
        "--min-tvl", "-t",
        type=float,
        default=500000.0,
        help="Minimum TVL (Total Value Locked) to include",
    )
    
    yield_parser.add_argument(
        "--max-results", "-r",
        type=int,
        default=5,
        help="Maximum number of results to display",
    )
    
    yield_parser.add_argument(
        "--name", "-n",
        default="YieldHunter",
        help="Name for the agent",
    )
    
    # Wallet management command
    wallet_parser = subparsers.add_parser(
        "wallet", 
        help="Manage cryptocurrency wallets"
    )
    
    wallet_subparsers = wallet_parser.add_subparsers(
        dest="wallet_command",
        help="Wallet command to run",
        required=True
    )
    
    # Create wallet command
    create_parser = wallet_subparsers.add_parser(
        "create", 
        help="Create a new wallet"
    )
    
    create_parser.add_argument(
        "chain",
        choices=["solana", "ethereum", "Solana", "Ethereum"],
        help="Blockchain for the wallet",
    )
    
    create_parser.add_argument(
        "name",
        help="Name for the wallet",
    )
    
    # Import wallet command
    import_parser = wallet_subparsers.add_parser(
        "import", 
        help="Import an existing wallet"
    )
    
    import_parser.add_argument(
        "chain",
        choices=["solana", "ethereum", "Solana", "Ethereum"],
        help="Blockchain for the wallet",
    )
    
    import_parser.add_argument(
        "name",
        help="Name for the wallet",
    )
    
    import_parser.add_argument(
        "private_key",
        help="Private key for the wallet",
    )
    
    # List wallets command
    list_parser = wallet_subparsers.add_parser(
        "list", 
        help="List all wallets"
    )
    
    # Get wallet balance command
    balance_parser = wallet_subparsers.add_parser(
        "balance", 
        help="Get wallet balance"
    )
    
    balance_parser.add_argument(
        "name",
        help="Name of the wallet",
    )
    
    # Delete wallet command
    delete_parser = wallet_subparsers.add_parser(
        "delete", 
        help="Delete a wallet"
    )
    
    delete_parser.add_argument(
        "name",
        help="Name of the wallet to delete",
    )
    
    # Token tracking command
    token_parser = subparsers.add_parser(
        "token", 
        help="Track and analyze tokens"
    )
    
    token_subparsers = token_parser.add_subparsers(
        dest="token_command",
        help="Token command to run",
        required=True
    )
    
    # Get token price command
    price_parser = token_subparsers.add_parser(
        "price", 
        help="Get token price"
    )
    
    price_parser.add_argument(
        "symbol",
        help="Token symbol (e.g., BTC, ETH, SOL)",
    )
    
    # Analyze token command
    analyze_parser = token_subparsers.add_parser(
        "analyze", 
        help="Analyze token data"
    )
    
    analyze_parser.add_argument(
        "symbol",
        help="Token symbol (e.g., BTC, ETH, SOL)",
    )
    
    analyze_parser.add_argument(
        "--llm",
        action="store_true",
        help="Use LLM to generate insights",
    )
    
    analyze_parser.add_argument(
        "--chart", "-c",
        action="store_true",
        help="Generate price chart",
    )
    
    analyze_parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="Number of days for historical data",
    )
    
    analyze_parser.add_argument(
        "--show", "-s",
        action="store_true",
        help="Show chart (requires GUI)",
    )
    
    # Portfolio analysis command
    portfolio_parser = token_subparsers.add_parser(
        "portfolio", 
        help="Analyze token portfolio"
    )
    
    portfolio_parser.add_argument(
        "wallets",
        nargs="+",
        help="Wallets to analyze in format 'chain:address' (e.g., ethereum:0x123...)",
    )
    
    portfolio_parser.add_argument(
        "--llm",
        action="store_true",
        help="Use LLM to generate portfolio report",
    )
    
    portfolio_parser.add_argument(
        "--chart", "-c",
        action="store_true",
        help="Generate portfolio distribution chart",
    )
    
    portfolio_parser.add_argument(
        "--show", "-s",
        action="store_true",
        help="Show chart (requires GUI)",
    )
    
    # Compare tokens command
    compare_parser = token_subparsers.add_parser(
        "compare", 
        help="Compare multiple tokens"
    )
    
    compare_parser.add_argument(
        "symbols",
        nargs="+",
        help="Token symbols to compare (e.g., BTC ETH SOL)",
    )
    
    compare_parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="Number of days for historical data",
    )
    
    compare_parser.add_argument(
        "--normalized", "-n",
        action="store_true",
        help="Normalize prices to percentage change",
    )
    
    compare_parser.add_argument(
        "--correlation", "-r",
        action="store_true",
        help="Generate correlation heatmap",
    )
    
    compare_parser.add_argument(
        "--show", "-s",
        action="store_true",
        help="Show charts (requires GUI)",
    )
    
    # Volatility comparison command
    volatility_parser = token_subparsers.add_parser(
        "volatility", 
        help="Compare token volatility"
    )
    
    volatility_parser.add_argument(
        "symbols",
        nargs="+",
        help="Token symbols to compare (e.g., BTC ETH SOL)",
    )
    
    volatility_parser.add_argument(
        "--show", "-s",
        action="store_true",
        help="Show chart (requires GUI)",
    )
    
    # LLM commands
    llm_parser = subparsers.add_parser(
        "llm", 
        help="LLM-powered analysis and insights"
    )
    
    llm_subparsers = llm_parser.add_subparsers(
        dest="llm_command",
        help="LLM command to run",
        required=True
    )
    
    # Market analysis command
    market_parser = llm_subparsers.add_parser(
        "market", 
        help="Generate market analysis using LLM"
    )
    
    market_parser.add_argument(
        "--output", "-o",
        help="Output file for the analysis (markdown format)",
    )
    
    # Strategy generation command
    strategy_parser = llm_subparsers.add_parser(
        "strategy", 
        help="Generate DeFi investment strategy using LLM"
    )
    
    strategy_parser.add_argument(
        "--chains", "-c",
        nargs="+",
        default=["Solana", "Ethereum"],
        help="Chains to include in the strategy",
    )
    
    strategy_parser.add_argument(
        "--risk-profile", "-r",
        choices=["conservative", "moderate", "aggressive"],
        default="moderate",
        help="Risk profile for the strategy",
    )
    
    strategy_parser.add_argument(
        "--amount", "-a",
        type=float,
        default=10000.0,
        help="Investment amount in USD",
    )
    
    strategy_parser.add_argument(
        "--min-yield", "-y",
        type=float,
        default=5.0,
        help="Minimum yield percentage to include",
    )
    
    strategy_parser.add_argument(
        "--min-tvl", "-t",
        type=float,
        default=500000.0,
        help="Minimum TVL to include",
    )
    
    strategy_parser.add_argument(
        "--max-opportunities", "-m",
        type=int,
        default=10,
        help="Maximum number of opportunities to consider",
    )
    
    strategy_parser.add_argument(
        "--output", "-o",
        help="Output file for the strategy (markdown format)",
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    # If no command specified, show help
    if not args.command:
        parser.print_help()
        return
    
    logger.info(f"Starting HiramAbiff CLI v{__version__}")
    
    # Handle commands
    if args.command == "yield":
        asyncio.run(
            run_yield_finder(
                chains=args.chains,
                min_yield=args.min_yield,
                min_tvl=args.min_tvl,
                max_results=args.max_results,
                agent_name=args.name,
            )
        )
    elif args.command == "wallet":
        asyncio.run(run_wallet_command(args))
    elif args.command == "token":
        asyncio.run(run_token_command(args))
    elif args.command == "llm":
        asyncio.run(run_llm_command(args))
    

if __name__ == "__main__":
    main() 