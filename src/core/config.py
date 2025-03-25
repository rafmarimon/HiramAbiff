"""
Configuration module for the HiramAbiff application.
Loads environment variables and provides configuration settings.
"""

import os
from pathlib import Path
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Base paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    # Application Settings
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"
    
    # Security Settings
    SECRET_KEY: str = "HIRAMABIFF_DEVELOPMENT_SECRET_KEY_REPLACE_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Database Settings - Optional for examples
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "hiramabiff"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_URI: Optional[PostgresDsn] = None
    
    @model_validator(mode="after")
    def assemble_postgres_uri(self) -> "Settings":
        if all([self.POSTGRES_HOST, self.POSTGRES_PORT, self.POSTGRES_DB, 
                self.POSTGRES_USER, self.POSTGRES_PASSWORD]):
            try:
                self.POSTGRES_URI = PostgresDsn.build(
                    scheme="postgresql",
                    username=self.POSTGRES_USER,
                    password=self.POSTGRES_PASSWORD,
                    host=self.POSTGRES_HOST,
                    port=self.POSTGRES_PORT,
                    path=f"{self.POSTGRES_DB}",
                )
            except Exception:
                # If URI can't be built (e.g., invalid credentials), leave as None
                pass
        return self
    
    # MongoDB Settings - Optional for examples
    MONGO_URI: str = "mongodb://localhost:27017/hiramabiff"
    
    # Redis Settings - Optional for examples
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_ENABLED: bool = False  # Set to True to enable Redis
    
    # Blockchain API Keys
    # Solana
    SOLANA_RPC_URL: str = "https://api.mainnet-beta.solana.com"
    SOLANA_RPC_URL_TESTNET: str = "https://api.testnet.solana.com"
    SOLANA_RPC_URL_DEVNET: str = "https://api.devnet.solana.com"
    
    # Ethereum
    ETHEREUM_RPC_URL: str = os.getenv("ETHEREUM_RPC_URL", "https://eth-mainnet.infura.io/v3/your-project-id")
    ETHEREUM_RPC_URL_TESTNET: str = os.getenv("ETHEREUM_RPC_URL_TESTNET", "https://eth-sepolia.infura.io/v3/your-project-id")
    
    # Check if Alchemy Solana URL is set, and use it for Ethereum if needed
    @model_validator(mode="after")
    def setup_alchemy_endpoints(self) -> "Settings":
        alchemy_key = os.getenv("ALCHEMY_API_KEY")
        if alchemy_key:
            # If we have an Alchemy key but no Ethereum RPC URL set via env var,
            # use the Alchemy key to create Ethereum endpoints
            if self.ETHEREUM_RPC_URL == "https://eth-mainnet.infura.io/v3/your-project-id":
                self.ETHEREUM_RPC_URL = f"https://eth-mainnet.g.alchemy.com/v2/{alchemy_key}"
            
            if self.ETHEREUM_RPC_URL_TESTNET == "https://eth-sepolia.infura.io/v3/your-project-id":
                self.ETHEREUM_RPC_URL_TESTNET = f"https://eth-sepolia.g.alchemy.com/v2/{alchemy_key}"
        
        return self
    
    # DeFi Data Sources
    DEFILLAMA_API_URL: str = "https://yields.llama.fi"
    DEFILLAMA_API_KEY: Optional[str] = None
    
    # ML Model Settings
    MODEL_STORAGE_PATH: str = str(BASE_DIR / "models")
    MODEL_RETRAIN_INTERVAL: int = 86400
    
    # Agent Settings
    AGENT_COLLABORATION_ENABLED: bool = True
    MAX_CONCURRENT_AGENTS: int = 5
    AGENT_TIMEOUT: int = 120
    
    # Security Settings
    TRANSACTION_MONITORING_ENABLED: bool = True
    MULTI_SIG_THRESHOLD: int = 2
    MAX_TRANSACTION_VALUE_WITHOUT_APPROVAL: float = 100.0
    
    # Web Interface
    WEB_DASHBOARD_ENABLED: bool = True
    WEB_API_ENABLED: bool = True
    
    # LLM Settings
    LLM_MODEL: str = "gpt-4"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 1000
    
    # LangChain Settings
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "hiramabiff-market-analysis"
    LANGCHAIN_TRACING_V2: bool = True
    
    # Report Settings
    REPORT_GENERATION_TIME: str = "08:00"  # Time to generate daily reports (24-hour format)
    REPORT_STORAGE_PATH: str = str(BASE_DIR / "reports")


# Create a global settings instance
settings = Settings() 