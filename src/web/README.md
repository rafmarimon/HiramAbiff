# HiramAbiff Dashboard

## Overview

The HiramAbiff Dashboard provides a web-based interface for monitoring and interacting with the HiramAbiff DeFi agent system. The dashboard integrates LangChain for advanced AI-powered market analysis and decision-making.

## Features

- **Overview**: Quick system status and market overview
- **Market Analysis**: AI-generated market reports and projections
- **Wallet Information**: Monitor wallet balances and transaction history
- **Settings**: Configure system parameters and API keys

## AI-Powered Market Analysis

The dashboard leverages LangChain and OpenAI to generate detailed market analysis reports, including:

- General market sentiment and trends
- DeFi sector analysis with yield opportunities
- Technical analysis and support/resistance levels
- News impact analysis
- Short and medium-term market projections

## Running the Dashboard

To run the dashboard:

```bash
# Activate the virtual environment
source venv/bin/activate

# Run the dashboard
python scripts/run_dashboard.py
```

The dashboard will be available at [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)

## API Keys

The dashboard requires the following API keys to be set in your `.env` file:

- `OPENAI_API_KEY`: For generating market analysis reports
- `LANGCHAIN_API_KEY`: For LangChain tracing and monitoring
- `ALCHEMY_API_KEY`: For blockchain data access

## Screenshot

[Dashboard Screenshot to be added] 

from langchain.llms import OpenAI
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent

# Create tools for the agent
tools = [
    Tool(
        name="Market Data",
        func=get_market_data,
        description="Get current market data for cryptocurrencies"
    )
]

# Initialize the LLM
llm = OpenAI(temperature=0.7, api_key=os.getenv("OPENAI_API_KEY"))

# Create the agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools) 