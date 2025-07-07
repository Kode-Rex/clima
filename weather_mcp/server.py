"""
Clima MCP Server - FastMCP implementation
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from fastmcp import FastMCP, Context
from loguru import logger

from .config import Config, get_config, setup_logging
from .accuweather import AccuWeatherClient


# Initialize FastMCP app
mcp = FastMCP("clima-mcp")


# Global weather client (will be initialized in main)
weather_client: Optional[AccuWeatherClient] = None


# Core business logic functions (for easy testing)
async def _search_locations_impl(query: str, language: str = "en-us") -> Dict[str, Any]:
    """Search for locations by name to get location keys for weather data"""
    if not weather_client:
        raise ValueError("Weather client not initialized")
    
    async with weather_client:
        locations = await weather_client.search_locations(query, language)
        return {
            "tool": "search_locations",
            "query": query,
            "results": locations
        }

async def _get_location_key_impl(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get AccuWeather location key from coordinates"""
    if not weather_client:
        raise ValueError("Weather client not initialized")
    
    async with weather_client:
        location_key = await weather_client.get_location_key(latitude, longitude)
        return {
            "tool": "get_location_key",
            "coordinates": {"latitude": latitude, "longitude": longitude},
            "location_key": location_key
        }

async def _get_current_weather_impl(location_key: str, details: bool = True) -> Dict[str, Any]:
    """Get current weather conditions for a location"""
    if not weather_client:
        raise ValueError("Weather client not initialized")
    
    async with weather_client:
        weather = await weather_client.get_current_weather(location_key, details)
        return {
            "tool": "get_current_weather",
            "location_key": location_key,
            "weather": {
                "temperature": weather.temperature,
                "temperature_unit": weather.temperature_unit,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
                "wind_direction": weather.wind_direction,
                "pressure": weather.pressure,
                "visibility": weather.visibility,
                "uv_index": weather.uv_index,
                "weather_text": weather.weather_text,
                "weather_icon": weather.weather_icon,
                "precipitation": weather.precipitation,
                "local_time": weather.local_time.isoformat()
            }
        }

async def _get_weather_forecast_impl(location_key: str, metric: bool = True) -> Dict[str, Any]:
    """Get 5-day weather forecast for a location"""
    if not weather_client:
        raise ValueError("Weather client not initialized")
    
    async with weather_client:
        forecast = await weather_client.get_5day_forecast(location_key, metric)
        return {
            "tool": "get_weather_forecast",
            "location_key": location_key,
            "forecast": [
                {
                    "date": f.date.isoformat(),
                    "day_temperature": f.day_temperature,
                    "night_temperature": f.night_temperature,
                    "day_weather_text": f.day_weather_text,
                    "night_weather_text": f.night_weather_text,
                    "day_icon": f.day_icon,
                    "night_icon": f.night_icon,
                    "precipitation_probability": f.precipitation_probability,
                    "wind_speed": f.wind_speed,
                    "wind_direction": f.wind_direction
                }
                for f in forecast
            ]
        }

async def _get_hourly_forecast_impl(location_key: str, hours: int = 12) -> Dict[str, Any]:
    """Get hourly weather forecast for a location"""
    if not weather_client:
        raise ValueError("Weather client not initialized")
    
    async with weather_client:
        forecast = await weather_client.get_hourly_forecast(location_key, hours)
        return {
            "tool": "get_hourly_forecast",
            "location_key": location_key,
            "hours": hours,
            "forecast": forecast
        }

async def _get_weather_alerts_impl(location_key: str) -> Dict[str, Any]:
    """Get weather alerts for a location"""
    if not weather_client:
        raise ValueError("Weather client not initialized")
    
    async with weather_client:
        alerts = await weather_client.get_weather_alerts(location_key)
        return {
            "tool": "get_weather_alerts",
            "location_key": location_key,
            "alerts": [
                {
                    "alert_id": alert.alert_id,
                    "title": alert.title,
                    "description": alert.description,
                    "severity": alert.severity,
                    "category": alert.category,
                    "start_time": alert.start_time.isoformat(),
                    "end_time": alert.end_time.isoformat() if alert.end_time else None,
                    "areas": alert.areas
                }
                for alert in alerts
            ]
        }

async def _get_weather_indices_impl(location_key: str, index_id: int = 1) -> Dict[str, Any]:
    """Get weather indices like air quality, UV index, etc."""
    if not weather_client:
        raise ValueError("Weather client not initialized")
    
    async with weather_client:
        indices = await weather_client.get_indices(location_key, index_id)
        return {
            "tool": "get_weather_indices",
            "location_key": location_key,
            "index_id": index_id,
            "indices": indices
        }

async def _get_historical_weather_impl(location_key: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Get historical weather data (requires premium API)"""
    if not weather_client:
        raise ValueError("Weather client not initialized")
    
    async with weather_client:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
        historical = await weather_client.get_historical_weather(location_key, start_dt, end_dt)
        return {
            "tool": "get_historical_weather",
            "location_key": location_key,
            "start_date": start_date,
            "end_date": end_date,
            "historical_data": historical
        }

@mcp.tool()
async def search_locations(query: str, language: str = "en-us") -> Dict[str, Any]:
    """Search for locations by name to get location keys for weather data"""
    return await _search_locations_impl(query, language)


@mcp.tool()
async def get_location_key(latitude: float, longitude: float) -> Dict[str, Any]:
    """Get AccuWeather location key from coordinates"""
    return await _get_location_key_impl(latitude, longitude)


@mcp.tool()
async def get_current_weather(location_key: str, details: bool = True) -> Dict[str, Any]:
    """Get current weather conditions for a location"""
    return await _get_current_weather_impl(location_key, details)


@mcp.tool()
async def get_weather_forecast(location_key: str, metric: bool = True) -> Dict[str, Any]:
    """Get 5-day weather forecast for a location"""
    return await _get_weather_forecast_impl(location_key, metric)


@mcp.tool()
async def get_hourly_forecast(location_key: str, hours: int = 12) -> Dict[str, Any]:
    """Get hourly weather forecast for a location"""
    return await _get_hourly_forecast_impl(location_key, hours)


@mcp.tool()
async def get_weather_alerts(location_key: str) -> Dict[str, Any]:
    """Get weather alerts for a location"""
    return await _get_weather_alerts_impl(location_key)


@mcp.tool()
async def get_weather_indices(location_key: str, index_id: int = 1) -> Dict[str, Any]:
    """Get weather indices like air quality, UV index, etc."""
    return await _get_weather_indices_impl(location_key, index_id)


@mcp.tool()
async def get_historical_weather(location_key: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """Get historical weather data (requires premium API)"""
    return await _get_historical_weather_impl(location_key, start_date, end_date)


# Note: FastMCP resources would require parameterized URIs
# For now, we're focusing on the tool functionality


def create_server(config: Optional[Config] = None) -> FastMCP:
    """Create and configure the FastMCP server"""
    global weather_client
    
    if not config:
        config = get_config()
    
    # Setup logging
    setup_logging(config)
    
    # Initialize weather client
    weather_client = AccuWeatherClient(config)
    
    logger.info("FastMCP Clima server initialized")
    return mcp


async def main():
    """Main entry point for the FastMCP server"""
    try:
        config = get_config()
        server = create_server(config)
        await server.run()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 