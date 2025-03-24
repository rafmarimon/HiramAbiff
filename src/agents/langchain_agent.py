"""
LangChain integration module for HiramAbiff.

This module provides LangChain-based agents for market analysis and reporting.
"""

import os
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.tools import Tool
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

from loguru import logger

from src.core.config import settings


class MarketAnalysisAgent:
    """
    LangChain-based agent for market analysis and reporting.
    """
    
    def __init__(self):
        """Initialize the MarketAnalysisAgent."""
        self.llm = self._initialize_llm()
        self.tools = self._initialize_tools()
        self.agent = self._initialize_agent()
        
        # Create reports directory if it doesn't exist
        os.makedirs(settings.REPORT_STORAGE_PATH, exist_ok=True)
    
    def _initialize_llm(self) -> ChatOpenAI:
        """Initialize the language model."""
        return ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def _initialize_tools(self) -> List[Tool]:
        """Initialize tools for the agent."""
        search = DuckDuckGoSearchAPIWrapper()
        
        tools = [
            Tool(
                name="Search",
                func=search.run,
                description="Useful for when you need to search for recent market information, news, or data."
            ),
            # Additional tools can be added here as needed
        ]
        
        return tools
    
    def _initialize_agent(self):
        """Initialize the LangChain agent."""
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
    
    async def generate_market_analysis(self) -> Dict[str, Any]:
        """
        Generate a market analysis report.
        
        Returns:
            Dict[str, Any]: A dictionary containing the market analysis.
        """
        logger.info("Generating market analysis...")
        
        prompt = """
        You are a financial analyst specialized in cryptocurrency and DeFi markets.
        
        Please provide a comprehensive daily market analysis including:
        
        1. Overall Market Summary:
           - General market sentiment (bullish, bearish, neutral)
           - Key market movements in the last 24 hours
           - Major cryptocurrency performance (BTC, ETH, SOL, etc.)
           
        2. DeFi Sector Analysis:
           - Major DeFi protocols performance
           - TVL changes in key protocols
           - Yield opportunities analysis
           
        3. News and Events Analysis:
           - Impact of recent news on market
           - Upcoming events that might affect the market
           
        4. Technical Analysis:
           - Support and resistance levels for major cryptocurrencies
           - Trend analysis and patterns
           
        5. Market Projections:
           - Short-term outlook (24-48 hours)
           - Medium-term outlook (1-2 weeks)
           - Potential opportunities and risks
        
        The report should be detailed yet concise, data-driven, and actionable for traders.
        Include specific numeric data where possible.
        
        Current date: {date}
        """
        
        try:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            result = self.agent.run(prompt.format(date=current_date))
            
            report = {
                "date": current_date,
                "content": result,
                "generated_at": datetime.datetime.now().isoformat(),
            }
            
            # Save the report
            self._save_report(report)
            
            return report
        
        except Exception as e:
            logger.error(f"Error generating market analysis: {e}")
            return {
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "content": f"Error generating market analysis: {str(e)}",
                "generated_at": datetime.datetime.now().isoformat(),
                "error": True
            }
    
    def _save_report(self, report: Dict[str, Any]) -> None:
        """
        Save the report to a file.
        
        Args:
            report: The report to save.
        """
        report_path = Path(settings.REPORT_STORAGE_PATH) / f"market_analysis_{report['date']}.json"
        
        import json
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved to {report_path}")
    
    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest market analysis report.
        
        Returns:
            Optional[Dict[str, Any]]: The latest report, or None if no reports exist.
        """
        try:
            reports_dir = Path(settings.REPORT_STORAGE_PATH)
            report_files = list(reports_dir.glob("market_analysis_*.json"))
            
            if not report_files:
                return None
            
            # Sort by modification time (newest first)
            latest_report_file = max(report_files, key=lambda p: p.stat().st_mtime)
            
            import json
            with open(latest_report_file, "r") as f:
                return json.load(f)
        
        except Exception as e:
            logger.error(f"Error getting latest report: {e}")
            return None


# Create a global instance of the agent
market_analysis_agent = MarketAnalysisAgent() 