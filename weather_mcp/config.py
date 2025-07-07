"""
Configuration management for Clima MCP server
"""

import os
from typing import Optional
from pathlib import Path
from pydantic import field_validator, ConfigDict
from pydantic_settings import BaseSettings
from loguru import logger


class Config(BaseSettings):
    """Configuration settings for Clima MCP server"""
    
    # AccuWeather API Configuration
    accuweather_api_key: str
    accuweather_base_url: str = "http://dataservice.accuweather.com"
    
    # Server Configuration
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: Optional[str] = None
    
    # SSE Configuration
    sse_heartbeat_interval: int = 30
    sse_max_connections: int = 100
    
    # Cache Configuration
    cache_ttl_seconds: int = 300
    cache_max_size: int = 1000
    
    model_config = ConfigDict(
        # Load from .env file if it exists
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Allow env file to be missing (will use environment variables or defaults)
        env_ignore_empty=True
    )
    
    @field_validator("accuweather_api_key")
    @classmethod
    def validate_api_key(cls, v):
        if not v or v == "your_api_key_here":
            raise ValueError("AccuWeather API key is required. Set ACCUWEATHER_API_KEY environment variable.")
        return v
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


def get_config() -> Config:
    """Get application configuration from .env file and environment variables"""
    try:
        # Check if .env file exists
        env_file = Path(".env")
        if not env_file.exists():
            logger.warning("No .env file found. Using environment variables or defaults.")
            logger.info("To create a .env file, copy env.example to .env and update with your values.")
        
        config = Config()
        logger.info("Configuration loaded successfully")
        
        # Validate that API key is set
        if config.accuweather_api_key == "your_api_key_here":
            logger.warning("AccuWeather API key not configured. Please set ACCUWEATHER_API_KEY in .env or environment.")
        
        return config
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        logger.error("Make sure to set ACCUWEATHER_API_KEY in .env file or environment variables")
        raise


def setup_logging(config: Config) -> None:
    """Setup logging configuration"""
    logger.remove()  # Remove default handler
    
    # Console handler
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=config.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # File handler (if specified)
    if config.log_file:
        os.makedirs(os.path.dirname(config.log_file), exist_ok=True)
        logger.add(
            sink=config.log_file,
            level=config.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="30 days"
        ) 