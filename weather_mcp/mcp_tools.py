"""
MCP tool handlers for weather operations using service-based architecture
"""

from typing import TYPE_CHECKING

from .models import (
    LocationQuery, LocationKey, ForecastQuery, 
    ExtendedForecastQuery, HourlyForecastQuery
)
from .services import (
    LocationService, WeatherService, ForecastService,
    AlertService, RawWeatherService
)

if TYPE_CHECKING:
    from .nws import NationalWeatherServiceClient


def setup_mcp_tools(mcp, weather_client: "NationalWeatherServiceClient"):
    """Setup all MCP tool handlers using service classes"""
    
    # Initialize services
    location_service = LocationService(weather_client)
    weather_service = WeatherService(weather_client)
    forecast_service = ForecastService(weather_client)
    alert_service = AlertService(weather_client)
    raw_weather_service = RawWeatherService(weather_client)
    
    @mcp.tool()
    async def search_locations(query: LocationQuery) -> dict:
        """Search for weather locations by name or ZIP code"""
        return await location_service.search_locations(query.query, query.language)

    @mcp.tool()
    async def get_current_weather(location: LocationKey) -> dict:
        """Get current weather conditions for a location"""
        return await weather_service.get_current_weather(location.location_key, location.details)

    @mcp.tool()
    async def get_5day_forecast(forecast: ForecastQuery) -> dict:
        """Get 5-day weather forecast for a location"""
        return await forecast_service.get_5day_forecast(forecast.location_key, forecast.metric)

    @mcp.tool()
    async def get_weather_alerts(location: LocationKey) -> dict:
        """Get weather alerts for a location"""
        return await alert_service.get_weather_alerts(location.location_key)

    @mcp.tool()
    async def get_location_weather(query: LocationQuery) -> dict:
        """Get current weather by searching for a location first"""
        return await location_service.get_location_weather(query.query, query.language)

    @mcp.tool()
    async def get_location_forecast(query: LocationQuery) -> dict:
        """Get 5-day forecast by searching for a location first"""
        return await location_service.get_location_forecast(query.query, query.language)

    @mcp.tool()
    async def get_location_alerts(query: LocationQuery) -> dict:
        """Get weather alerts by searching for a location first"""
        return await location_service.get_location_alerts(query.query, query.language)

    @mcp.tool()
    async def get_7day_forecast(forecast: ForecastQuery) -> dict:
        """Get 7-day weather forecast for a location"""
        return await forecast_service.get_extended_forecast(forecast.location_key, days=7, metric=forecast.metric)

    @mcp.tool()
    async def get_extended_forecast(forecast: ExtendedForecastQuery) -> dict:
        """Get extended weather forecast for a location (up to 7 days)"""
        return await forecast_service.get_extended_forecast(forecast.location_key, forecast.days, forecast.metric)

    @mcp.tool()
    async def get_hourly_forecast(forecast: HourlyForecastQuery) -> dict:
        """Get hourly weather forecast for a location (up to 168 hours/7 days)"""
        return await forecast_service.get_hourly_forecast(forecast.location_key, forecast.hours, forecast.metric)

    @mcp.tool()
    async def get_detailed_grid_data(location: LocationKey) -> dict:
        """Get detailed raw meteorological data with comprehensive weather parameters"""
        return await raw_weather_service.get_detailed_grid_data(location.location_key, metric=True)

    @mcp.tool()
    async def get_location_extended_forecast(query: LocationQuery) -> dict:
        """Get 7-day forecast by searching for a location first"""
        return await location_service.get_location_extended_forecast(query.query, days=7, language=query.language)

    @mcp.tool()
    async def get_location_hourly_forecast(query: LocationQuery) -> dict:
        """Get hourly forecast by searching for a location first"""
        return await location_service.get_location_hourly_forecast(query.query, hours=168, language=query.language)