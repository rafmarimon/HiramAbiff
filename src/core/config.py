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
    SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION: int = 86400
    CORS_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://localhost:8000"]
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        return v
    
    # Database Settings
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_URI: Optional[PostgresDsn] = None
    
    @model_validator(mode="after")
    def assemble_postgres_uri(self) -> "Settings":
        self.POSTGRES_URI = PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_HOST,
            port=self.POSTGRES_PORT,
            path=f"{self.POSTGRES_DB}",
        )
        return self
    
    # MongoDB Settings
    MONGO_URI: str
    
    # Redis Settings
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int
    REDIS_PASSWORD: Optional[str] = None
    
    # Blockchain API Keys
    # Solana
    SOLANA_RPC_URL: str
    SOLANA_RPC_URL_TESTNET: str
    SOLANA_RPC_URL_DEVNET: str
    
    # Ethereum
    ETHEREUM_RPC_URL: str
    ETHEREUM_RPC_URL_TESTNET: str
    
    # DeFi Data Sources
    DEFILLAMA_API_URL: str
    DEFILLAMA_API_KEY: Optional[str] = None
    
    # ML Model Settings
    MODEL_STORAGE_PATH: str
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


# Create a global settings instance
settings = Settings() 