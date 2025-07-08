"""
Weather MCP - National Weather Service Edition
Free weather data and alerts using NWS API
"""

__version__ = "1.0.0"
__author__ = "Weather MCP Team"

from .config import Config
from .nws import NationalWeatherServiceClient

__all__ = ["Config", "NationalWeatherServiceClient"]
