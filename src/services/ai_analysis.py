"""
AI market analysis service for HiramAbiff.

This module provides functionality for generating AI-powered market analysis.
"""

import os
import json
import time
import datetime
import asyncio
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from loguru import logger

try:
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain_openai import ChatOpenAI
    from langchain.output_parsers import StructuredOutputParser, ResponseSchema
    LANGCHAIN_AVAILABLE = True
except ImportError:
    logger.warning("LangChain not available. Using mock AI analysis.")
    LANGCHAIN_AVAILABLE = False

# Load environment variables
load_dotenv()

class AIMarketAnalysisService:
    """Service for generating AI-powered market analysis."""
    
    def __init__(self):
        """Initialize the AI market analysis service."""
        self.reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = self._initialize_llm() if LANGCHAIN_AVAILABLE and self.openai_api_key else None
        
        # Track report generation
        self.is_generating = False
        self.latest_report = None
        
        # Load the latest report if available
        self._load_latest_report()
    
    def _initialize_llm(self):
        """Initialize the LLM for market analysis."""
        if not LANGCHAIN_AVAILABLE:
            return None
        
        try:
            return ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                api_key=self.openai_api_key
            )
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            return None
    
    def _load_latest_report(self):
        """Load the latest report from disk."""
        try:
            # Find the most recent report file
            report_files = [f for f in os.listdir(self.reports_dir) if f.endswith('.json')]
            if not report_files:
                return
            
            # Sort by date (filename format: report_YYYY-MM-DD.json)
            report_files.sort(reverse=True)
            latest_file = os.path.join(self.reports_dir, report_files[0])
            
            with open(latest_file, 'r') as f:
                self.latest_report = json.load(f)
            
            logger.info(f"Loaded latest report from {latest_file}")
        except Exception as e:
            logger.error(f"Error loading latest report: {e}")
    
    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """
        Get the latest market analysis report.
        
        Returns:
            Dictionary containing the latest report or None if not available
        """
        if self.latest_report:
            return self.latest_report
        else:
            return self._get_mock_report()
    
    async def generate_market_analysis(self) -> Optional[Dict[str, Any]]:
        """
        Generate a new market analysis report using AI.
        
        Returns:
            The generated report or None if generation failed
        """
        if self.is_generating:
            logger.info("Report generation already in progress")
            return None
        
        self.is_generating = True
        logger.info("Starting market analysis report generation")
        
        try:
            # Check if we can use LangChain
            if not LANGCHAIN_AVAILABLE or not self.llm or not self.openai_api_key:
                logger.warning("Using mock report generation")
                await asyncio.sleep(3)  # Simulate processing time
                self.latest_report = self._get_mock_report()
                self.is_generating = False
                return self.latest_report
            
            # Define the schema for structured output
            response_schemas = [
                ResponseSchema(name="market_overview", description="General overview of the cryptocurrency market"),
                ResponseSchema(name="key_observations", description="Key observations about market trends"),
                ResponseSchema(name="market_predictions", description="Predictions for the cryptocurrency market"),
                ResponseSchema(name="investment_opportunities", description="Potential investment opportunities"),
            ]
            
            output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
            format_instructions = output_parser.get_format_instructions()
            
            # Create prompt for market analysis
            prompt = PromptTemplate(
                template="""You are a cryptocurrency market analysis expert. Analyze the current market trends and provide insights.

{format_instructions}

Current date: {date}

Provide a comprehensive market analysis covering:
1. Market overview
2. Key observations
3. Market predictions
4. Investment opportunities

Focus especially on Bitcoin, Ethereum, and Solana.
""",
                input_variables=["date"],
                partial_variables={"format_instructions": format_instructions}
            )
            
            # Create the chain
            chain = LLMChain(llm=self.llm, prompt=prompt)
            
            # Run the chain
            current_date = datetime.datetime.now().strftime("%Y-%m-%d")
            result = await chain.arun(date=current_date)
            
            # Parse the result
            try:
                parsed_result = output_parser.parse(result)
                
                # Format the report
                report = {
                    "generated_at": datetime.datetime.now().isoformat(),
                    "date": current_date,
                    "content": f"""# Market Analysis Report

## Market Overview
{parsed_result['market_overview']}

## Key Observations
{parsed_result['key_observations']}

## Market Predictions
{parsed_result['market_predictions']}

## Investment Opportunities
{parsed_result['investment_opportunities']}"""
                }
                
                # Save the report
                filename = os.path.join(self.reports_dir, f"report_{current_date}.json")
                with open(filename, 'w') as f:
                    json.dump(report, f, indent=2)
                
                self.latest_report = report
                logger.info(f"Generated new market analysis report: {filename}")
                
                self.is_generating = False
                return report
                
            except Exception as e:
                logger.error(f"Error parsing LLM result: {e}")
                self.is_generating = False
                return self._get_mock_report()
            
        except Exception as e:
            logger.error(f"Error generating market analysis: {e}")
            self.is_generating = False
            return self._get_mock_report()
    
    def _get_mock_report(self) -> Dict[str, Any]:
        """
        Get a mock report when AI generation is not available.
        
        Returns:
            A mock report dictionary
        """
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        return {
            "generated_at": datetime.datetime.now().isoformat(),
            "date": current_date,
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
Solana's ecosystem continues to grow despite recent technical challenges. Projects building on its infrastructure may present interesting investment opportunities due to lower fees and high throughput capabilities."""
        }


# Create a global AI market analysis service instance
ai_analysis_service = AIMarketAnalysisService() 