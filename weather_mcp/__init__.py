"""
Weather MCP - National Weather Service Edition
Free weather data and alerts using NWS API
"""

from ._version import __version__

__author__ = "Weather MCP Team"

from .config import Config
from .nws import NationalWeatherServiceClient

__all__ = ["Config", "NationalWeatherServiceClient", "__version__"]
