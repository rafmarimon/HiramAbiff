#!/usr/bin/env python
"""
LLM Analyzer Module

This module integrates with OpenAI's API to provide insights and analysis
on token data, market trends, and investment strategies.
"""

import os
import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import aiohttp
from loguru import logger
from dotenv import load_dotenv

# Try to load environment variables
load_dotenv()

class LLMAnalyzer:
    """A class for analyzing cryptocurrency data using large language models."""
    
    def __init__(self, reports_dir: str = None):
        """Initialize the LLM analyzer.
        
        Args:
            reports_dir: Directory for storing analysis reports
        """
        # Set up reports directory
        if reports_dir is None:
            home_dir = os.path.expanduser("~")
            self.reports_dir = os.path.join(home_dir, ".hiramabiff", "reports")
        else:
            self.reports_dir = reports_dir
            
        # Create reports directory if it doesn't exist
        os.makedirs(self.reports_dir, exist_ok=True)
        
        # Load API key from environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OpenAI API key not found. Set OPENAI_API_KEY in .env")
        
        # Configure model settings
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "2000"))
        
    async def call_openai_api(self, messages: List[Dict[str, str]]) -> str:
        """Call the OpenAI API with a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Response text from the model
            
        Raises:
            ValueError: If API call fails
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY in .env")
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    
                    if "choices" in result and len(result["choices"]) > 0:
                        return result["choices"][0]["message"]["content"]
                    else:
                        raise ValueError("No response generated from OpenAI API")
                        
        except aiohttp.ClientResponseError as e:
            logger.error(f"Error from OpenAI API: {e.status} - {e.message}")
            try:
                error_data = await e.response.json()
                logger.error(f"API error details: {error_data}")
            except:
                pass
            raise ValueError(f"API error: {e.status} - {e.message}")
            
        except aiohttp.ClientError as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise ValueError(f"Error calling OpenAI API: {str(e)}")
            
    async def analyze_token_data(self, token_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze token data using an LLM.
        
        Args:
            token_data: Token data from the TokenTracker
            
        Returns:
            Dict containing the original token data and LLM analysis
        """
        logger.info(f"Analyzing token data for {token_data['symbol']} using LLM")
        
        # Prepare prompt for the LLM
        system_message = {
            "role": "system",
            "content": (
                "You are a cryptocurrency and financial analysis expert. "
                "You provide insightful, accurate, and balanced analysis of cryptocurrency token data. "
                "Your analysis should include price trends, market position, potential risks and opportunities, "
                "and general market context. Be fact-based and avoid excessive speculation."
            )
        }
        
        user_message = {
            "role": "user",
            "content": (
                f"Please analyze the following data for {token_data['symbol']} and provide insights:\n\n"
                f"Current Price: ${token_data['current_price_usd']:.4f}\n"
                f"Market Cap: ${token_data['market_cap_usd']:,.2f}\n"
                f"24h Volume: ${token_data.get('volume_24h_usd', 0):,.2f}\n"
                f"24h Change: {token_data['change_24h_percent']:.2f}%\n"
                f"7d Change: {token_data.get('change_7d_percent', 0):.2f}%\n\n"
                f"30-Day Statistics:\n"
                f"- Average Price: ${token_data['stats']['mean_price_30d']:.4f}\n"
                f"- Min Price: ${token_data['stats']['min_price_30d']:.4f}\n"
                f"- Max Price: ${token_data['stats']['max_price_30d']:.4f}\n"
                f"- Volatility: {token_data['stats']['volatility_30d']:.4f}\n\n"
                "Please provide an analysis that covers:\n"
                "1. Price performance and volatility assessment\n"
                "2. Market position and relative strength\n"
                "3. Key factors potentially driving recent price action\n"
                "4. Potential short and medium-term outlook\n"
                "5. Notable risks and considerations for investors"
            )
        }
        
        # Call OpenAI API
        analysis_text = await self.call_openai_api([system_message, user_message])
        
        # Combine original data with analysis
        result = {
            **token_data,
            "llm_analysis": {
                "text": analysis_text,
                "model": self.model,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Save analysis to file
        report_file = f"{token_data['symbol'].lower()}_llm_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        report_path = os.path.join(self.reports_dir, report_file)
        
        with open(report_path, "w") as f:
            json.dump(result, f, indent=2)
        
        return result
    
    async def generate_portfolio_report(
        self, 
        portfolio_data: Dict[str, Any],
        market_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a comprehensive report for a cryptocurrency portfolio.
        
        Args:
            portfolio_data: Portfolio analysis data from TokenTracker
            market_context: Optional market context information
            
        Returns:
            Dict containing the portfolio report
        """
        logger.info("Generating portfolio report using LLM")
        
        # Prepare prompt for the LLM
        system_message = {
            "role": "system",
            "content": (
                "You are a cryptocurrency portfolio analyst and investment advisor. "
                "You provide insightful, balanced, and personalized analysis of cryptocurrency portfolios. "
                "Your analysis should include portfolio composition, diversification assessment, risk exposure, "
                "and allocation recommendations. Be fact-based and acknowledge the inherent uncertainty in cryptocurrency markets."
            )
        }
        
        # Build portfolio description for prompt
        portfolio_description = (
            f"Total Portfolio Value: ${portfolio_data['total_value_usd']:,.2f}\n\n"
            f"Token Distribution:\n"
        )
        
        for token, info in portfolio_data.get('token_distribution', {}).items():
            portfolio_description += (
                f"- {token}: {info.get('percentage', 0):.2f}% (${info.get('value_usd', 0):,.2f})\n"
            )
        
        # Add market context if available
        market_context_str = ""
        if market_context:
            market_context_str = (
                "\nMarket Context:\n"
                f"- Bitcoin Price: ${market_context.get('btc_price', 0):,.2f}\n"
                f"- Ethereum Price: ${market_context.get('eth_price', 0):,.2f}\n"
                f"- Current Market Trend: {market_context.get('market_trend', 'Unknown')}\n"
            )
        
        user_message = {
            "role": "user",
            "content": (
                f"Please analyze the following cryptocurrency portfolio and provide insights:\n\n"
                f"{portfolio_description}\n"
                f"{market_context_str}\n"
                "Please provide a comprehensive portfolio analysis that covers:\n"
                "1. Overall portfolio composition assessment and diversification\n"
                "2. Risk exposure and volatility analysis\n"
                "3. Allocation recommendations (what might be overweighted or underweighted)\n"
                "4. Suggested portfolio adjustments for different market scenarios\n"
                "5. Key risks and considerations for the current portfolio"
            )
        }
        
        # Call OpenAI API
        report_text = await self.call_openai_api([system_message, user_message])
        
        # Create report
        result = {
            "portfolio_data": portfolio_data,
            "llm_report": {
                "text": report_text,
                "model": self.model,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Save report to file
        report_file = f"portfolio_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        report_path = os.path.join(self.reports_dir, report_file)
        
        with open(report_path, "w") as f:
            json.dump(result, f, indent=2)
        
        return result
    
    async def generate_defi_strategy(
        self,
        opportunities: List[Dict[str, Any]],
        risk_profile: str = "moderate",
        investment_amount: float = 10000.0
    ) -> Dict[str, Any]:
        """Generate a DeFi investment strategy based on opportunities.
        
        Args:
            opportunities: List of DeFi opportunities (from a DeFi agent)
            risk_profile: Risk profile (conservative, moderate, aggressive)
            investment_amount: Amount to invest in USD
            
        Returns:
            Dict containing the strategy
        """
        logger.info(f"Generating {risk_profile} DeFi strategy for ${investment_amount:,.2f}")
        
        # Prepare prompt for the LLM
        system_message = {
            "role": "system",
            "content": (
                "You are a DeFi investment strategist specializing in yield opportunities. "
                "You provide clear, actionable strategies for investing in DeFi protocols based on "
                "risk tolerance, investment amount, and available opportunities. "
                "Your advice should be balanced, acknowledging risks while pursuing appropriate yields."
            )
        }
        
        # Build opportunities description
        opportunities_description = "Available Opportunities:\n\n"
        
        for i, opp in enumerate(opportunities, 1):
            opportunities_description += (
                f"{i}. {opp.get('protocol', 'Unknown Protocol')} on {opp.get('chain', 'Unknown Chain')}\n"
                f"   - APY: {opp.get('apy', 0):.2f}%\n"
                f"   - TVL: ${opp.get('tvl', 0):,.2f}\n"
                f"   - Token: {opp.get('token', 'Unknown')}\n"
                f"   - Strategy Type: {opp.get('strategy_type', 'Unknown')}\n\n"
            )
        
        user_message = {
            "role": "user",
            "content": (
                f"Please create a DeFi investment strategy with the following parameters:\n\n"
                f"Investment Amount: ${investment_amount:,.2f}\n"
                f"Risk Profile: {risk_profile.title()}\n\n"
                f"{opportunities_description}\n"
                "Please provide a detailed investment strategy that includes:\n"
                "1. Allocation recommendations across the opportunities (specify exact USD amounts)\n"
                "2. Rationale for each allocation based on risk profile\n"
                "3. Expected total yield and comparison to traditional finance alternatives\n"
                "4. Risk mitigation approaches and considerations\n"
                "5. Recommended monitoring and rebalancing strategy"
            )
        }
        
        # Call OpenAI API
        strategy_text = await self.call_openai_api([system_message, user_message])
        
        # Create strategy result
        result = {
            "parameters": {
                "risk_profile": risk_profile,
                "investment_amount": investment_amount,
                "opportunities_count": len(opportunities)
            },
            "opportunities": opportunities,
            "llm_strategy": {
                "text": strategy_text,
                "model": self.model,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Save strategy to file
        strategy_file = f"defi_strategy_{risk_profile}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        strategy_path = os.path.join(self.reports_dir, strategy_file)
        
        with open(strategy_path, "w") as f:
            json.dump(result, f, indent=2)
        
        return result
    
    async def analyze_market_trend(self) -> Dict[str, Any]:
        """Analyze overall market trends using an LLM.
        
        Returns:
            Dict containing the market analysis
        """
        logger.info("Generating market trend analysis using LLM")
        
        # Prepare prompt for the LLM
        system_message = {
            "role": "system",
            "content": (
                "You are a cryptocurrency market analyst with deep expertise in blockchain technology and markets. "
                "You provide balanced, insightful analysis of current market trends based on your knowledge. "
                "Your analysis should cover major tokens (like Bitcoin and Ethereum), sector trends, "
                "regulatory developments, and technical factors. Be balanced in your assessment, "
                "acknowledging both bullish and bearish factors."
            )
        }
        
        user_message = {
            "role": "user",
            "content": (
                "Please provide a comprehensive analysis of the current cryptocurrency market trends. "
                "Your analysis should cover:\n\n"
                "1. Major cryptocurrencies (Bitcoin, Ethereum, etc.) and their recent performance\n"
                "2. Market sectors showing strength or weakness (DeFi, NFTs, Layer-1s, etc.)\n"
                "3. Key technical indicators and market sentiment\n"
                "4. Relevant macroeconomic factors and regulatory developments\n"
                "5. Potential catalysts that could impact the market in the near term\n"
                "6. Overall market outlook and key trends to watch\n\n"
                "Please base your analysis on available knowledge and present a balanced view of the market."
            )
        }
        
        # Call OpenAI API
        analysis_text = await self.call_openai_api([system_message, user_message])
        
        # Create analysis result
        result = {
            "llm_analysis": {
                "text": analysis_text,
                "model": self.model,
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        # Save analysis to file
        analysis_file = f"market_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        analysis_path = os.path.join(self.reports_dir, analysis_file)
        
        with open(analysis_path, "w") as f:
            json.dump(result, f, indent=2)
        
        return result 