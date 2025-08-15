"""
Weather API Server - National Weather Service Edition
Free weather data and alerts using NWS API
"""

from ._version import __version__

__author__ = "Weather MCP Team"

# Core components
from .config import Config, get_config, setup_logging

# Models
from .models import (
    ExtendedForecastQuery,
    ForecastQuery,
    HourlyForecastQuery,
    LocationKey,
    LocationQuery,
)
from .nws import (
    CurrentWeather,
    NationalWeatherServiceClient,
    WeatherAlert,
    WeatherLocation,
)

# Services
from .services import (
    AlertService,
    ForecastService,
    LocationService,
    RawWeatherService,
    WeatherService,
    WeatherTestingService,
)

__all__ = [
    # Version
    "__version__",
    # Core
    "Config",
    "get_config",
    "setup_logging",
    "NationalWeatherServiceClient",
    "WeatherAlert",
    "WeatherLocation",
    "CurrentWeather",
    # Services
    "AlertService",
    "ForecastService",
    "LocationService",
    "RawWeatherService",
    "WeatherService",
    "WeatherTestingService",
    # Models
    "ExtendedForecastQuery",
    "ForecastQuery",
    "HourlyForecastQuery",
    "LocationKey",
    "LocationQuery",
]
