"""
MCP tool handlers for weather operations
"""

from typing import TYPE_CHECKING

from .models import (
    LocationQuery, LocationKey, ForecastQuery, 
    ExtendedForecastQuery, HourlyForecastQuery
)
from .implementations import (
    search_locations_impl, get_current_weather_impl, get_5day_forecast_impl,
    get_weather_alerts_impl, get_location_weather_impl, get_location_forecast_impl,
    get_location_alerts_impl, get_extended_forecast_impl, get_hourly_forecast_impl,
    get_detailed_grid_data_impl, get_location_extended_forecast_impl, 
    get_location_hourly_forecast_impl
)

if TYPE_CHECKING:
    from .nws import NationalWeatherServiceClient


def setup_mcp_tools(mcp, weather_client: "NationalWeatherServiceClient"):
    """Setup all MCP tool handlers"""
    
    @mcp.tool()
    async def search_locations(query: LocationQuery) -> dict:
        """Search for weather locations by name or ZIP code"""
        return await search_locations_impl(weather_client, query.query, query.language)

    @mcp.tool()
    async def get_current_weather(location: LocationKey) -> dict:
        """Get current weather conditions for a location"""
        return await get_current_weather_impl(weather_client, location.location_key, location.details)

    @mcp.tool()
    async def get_5day_forecast(forecast: ForecastQuery) -> dict:
        """Get 5-day weather forecast for a location"""
        return await get_5day_forecast_impl(weather_client, forecast.location_key, forecast.metric)

    @mcp.tool()
    async def get_weather_alerts(location: LocationKey) -> dict:
        """Get weather alerts for a location"""
        return await get_weather_alerts_impl(weather_client, location.location_key)

    @mcp.tool()
    async def get_location_weather(query: LocationQuery) -> dict:
        """Get current weather by searching for a location first"""
        return await get_location_weather_impl(weather_client, query.query, query.language)

    @mcp.tool()
    async def get_location_forecast(query: LocationQuery) -> dict:
        """Get 5-day forecast by searching for a location first"""
        return await get_location_forecast_impl(weather_client, query.query, query.language)

    @mcp.tool()
    async def get_location_alerts(query: LocationQuery) -> dict:
        """Get weather alerts by searching for a location first"""
        return await get_location_alerts_impl(weather_client, query.query, query.language)

    @mcp.tool()
    async def get_7day_forecast(forecast: ForecastQuery) -> dict:
        """Get 7-day weather forecast for a location"""
        return await get_extended_forecast_impl(weather_client, forecast.location_key, days=7, metric=forecast.metric)

    @mcp.tool()
    async def get_extended_forecast(forecast: ExtendedForecastQuery) -> dict:
        """Get extended weather forecast for a location (up to 7 days)"""
        return await get_extended_forecast_impl(weather_client, forecast.location_key, forecast.days, forecast.metric)

    @mcp.tool()
    async def get_hourly_forecast(forecast: HourlyForecastQuery) -> dict:
        """Get hourly weather forecast for a location (up to 168 hours/7 days)"""
        return await get_hourly_forecast_impl(weather_client, forecast.location_key, forecast.hours, forecast.metric)

    @mcp.tool()
    async def get_detailed_grid_data(location: LocationKey) -> dict:
        """Get detailed grid forecast data with comprehensive weather parameters"""
        return await get_detailed_grid_data_impl(weather_client, location.location_key, metric=True)

    @mcp.tool()
    async def get_location_extended_forecast(query: LocationQuery) -> dict:
        """Get 7-day forecast by searching for a location first"""
        return await get_location_extended_forecast_impl(weather_client, query.query, days=7, language=query.language)

    @mcp.tool()
    async def get_location_hourly_forecast(query: LocationQuery) -> dict:
        """Get hourly forecast by searching for a location first"""
        return await get_location_hourly_forecast_impl(weather_client, query.query, hours=168, language=query.language)
