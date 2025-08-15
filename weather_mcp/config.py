"""
Configuration management for Weather MCP Server
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Application configuration with environment variable support"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Ignore unknown fields from .env
    )

    # Server settings
    host: str = Field("0.0.0.0", description="Server host address")
    port: int = Field(8000, description="Server port")
    debug: bool = Field(False, description="Enable debug mode")
    log_level: str = Field("INFO", description="Logging level")

    # NWS API settings (no API key required - government service)
    nws_base_url: str = Field(
        "https://api.weather.gov", description="National Weather Service API base URL"
    )
    nominatim_base_url: str = Field(
        "https://nominatim.openstreetmap.org",
        description="Nominatim geocoding service URL",
    )

    # Cache settings
    cache_ttl_seconds: int = Field(300, description="Cache TTL in seconds (5 minutes)")
    cache_max_size: int = Field(1000, description="Maximum cache size")

    # Rate limiting
    rate_limit_per_minute: int = Field(60, description="API requests per minute")

    # Alert settings
    alert_check_interval: int = Field(60, description="Alert check interval in seconds")

    # SSE Server settings
    sse_heartbeat_interval: int = Field(
        30, description="SSE heartbeat interval in seconds"
    )
    sse_max_connections: int = Field(100, description="Maximum SSE connections")
    sse_connection_timeout: int = Field(
        300, description="SSE connection timeout in seconds"
    )


def get_config() -> Config:
    """Get configuration instance"""
    return Config()


def setup_logging(config: Config):
    """Setup logging configuration"""
    import sys

    from loguru import logger

    # Remove default logger
    logger.remove()

    # Add new logger with custom format
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level=config.log_level,
        colorize=True,
    )
