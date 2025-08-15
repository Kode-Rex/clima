"""
Custom exceptions for Weather MCP
"""


class WeatherMCPError(Exception):
    """Base exception for Weather MCP errors"""

    def __init__(self, message: str, error_code: str | None = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class APIError(WeatherMCPError):
    """Raised when external API calls fail"""

    pass


class LocationNotFoundError(WeatherMCPError):
    """Raised when location cannot be found"""

    pass


class WeatherDataError(WeatherMCPError):
    """Raised when weather data is invalid or unavailable"""

    pass


class ConfigurationError(WeatherMCPError):
    """Raised when configuration is invalid"""

    pass


class CacheError(WeatherMCPError):
    """Raised when cache operations fail"""

    pass


class SSEConnectionError(WeatherMCPError):
    """Raised when SSE connection fails"""

    pass


class RateLimitError(APIError):
    """Raised when API rate limit is exceeded"""

    pass


class AuthenticationError(APIError):
    """Raised when API authentication fails"""

    pass
