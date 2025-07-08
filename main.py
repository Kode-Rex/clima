#!/usr/bin/env python3
"""
Weather MCP Server - National Weather Service Edition
Provides weather data and alerts using free NWS API
"""

import asyncio
import sys
from contextlib import asynccontextmanager
from typing import Optional

from fastmcp import FastMCP
from pydantic import BaseModel, Field
from loguru import logger

from weather_mcp.config import Config
from weather_mcp.nws import NationalWeatherServiceClient
from weather_mcp.sse import WeatherSSEApp

# Configure logging
logger.remove()
logger.add(sys.stderr, format="{time} | {level} | {name}:{function}:{line} - {message}", level="INFO")

# Initialize FastMCP
mcp = FastMCP("Weather MCP")

# Global weather client
weather_client: Optional[NationalWeatherServiceClient] = None


class LocationQuery(BaseModel):
    """Location search query"""
    query: str = Field(..., description="Location name or ZIP code to search for")
    language: str = Field("en-us", description="Language code for results")


class LocationKey(BaseModel):
    """Location key for weather data"""
    location_key: str = Field(..., description="Location identifier (lat,lon format)")
    details: bool = Field(True, description="Include detailed weather information")


class ForecastQuery(BaseModel):
    """Forecast query parameters"""
    location_key: str = Field(..., description="Location identifier (lat,lon format)")
    metric: bool = Field(True, description="Use metric units (Celsius)")


# Implementation functions for testing
async def _search_locations_impl(query: str, language: str = "en-us") -> dict:
    """Implementation function for search_locations"""
    try:
        results = await weather_client.search_locations(query, language)
        return {
            "success": True,
            "locations": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Location search failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_current_weather_impl(location_key: str, details: bool = True) -> dict:
    """Implementation function for get_current_weather"""
    try:
        weather = await weather_client.get_current_weather(location_key, details)
        return {
            "success": True,
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
    except Exception as e:
        logger.error(f"Current weather failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_5day_forecast_impl(location_key: str, metric: bool = True) -> dict:
    """Implementation function for get_5day_forecast"""
    try:
        forecasts = await weather_client.get_5day_forecast(location_key, metric)
        return {
            "success": True,
            "forecasts": [
                {
                    "date": f.date.isoformat(),
                    "min_temperature": f.min_temperature,
                    "max_temperature": f.max_temperature,
                    "temperature_unit": f.temperature_unit,
                    "day_weather_text": f.day_weather_text,
                    "day_weather_icon": f.day_weather_icon,
                    "day_precipitation_probability": f.day_precipitation_probability,
                    "night_weather_text": f.night_weather_text,
                    "night_weather_icon": f.night_weather_icon,
                    "night_precipitation_probability": f.night_precipitation_probability
                }
                for f in forecasts
            ],
            "count": len(forecasts)
        }
    except Exception as e:
        logger.error(f"5-day forecast failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_weather_alerts_impl(location_key: str) -> dict:
    """Implementation function for get_weather_alerts"""
    try:
        alerts = await weather_client.get_weather_alerts(location_key)
        return {
            "success": True,
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
            ],
            "count": len(alerts)
        }
    except Exception as e:
        logger.error(f"Weather alerts failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_location_weather_impl(query: str, language: str = "en-us") -> dict:
    """Implementation function for get_location_weather"""
    try:
        # Search for location
        locations = await weather_client.search_locations(query, language)
        if not locations:
            return {"success": False, "error": f"No locations found for '{query}'"}
        
        # Get weather for first location
        location_key = locations[0]["Key"]
        weather = await weather_client.get_current_weather(location_key, True)
        
        return {
            "success": True,
            "location": locations[0],
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
    except Exception as e:
        logger.error(f"Location weather failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_location_forecast_impl(query: str, language: str = "en-us") -> dict:
    """Implementation function for get_location_forecast"""
    try:
        # Search for location
        locations = await weather_client.search_locations(query, language)
        if not locations:
            return {"success": False, "error": f"No locations found for '{query}'"}
        
        # Get forecast for first location
        location_key = locations[0]["Key"]
        forecasts = await weather_client.get_5day_forecast(location_key, True)
        
        return {
            "success": True,
            "location": locations[0],
            "forecasts": [
                {
                    "date": f.date.isoformat(),
                    "min_temperature": f.min_temperature,
                    "max_temperature": f.max_temperature,
                    "temperature_unit": f.temperature_unit,
                    "day_weather_text": f.day_weather_text,
                    "day_weather_icon": f.day_weather_icon,
                    "day_precipitation_probability": f.day_precipitation_probability,
                    "night_weather_text": f.night_weather_text,
                    "night_weather_icon": f.night_weather_icon,
                    "night_precipitation_probability": f.night_precipitation_probability
                }
                for f in forecasts
            ],
            "count": len(forecasts)
        }
    except Exception as e:
        logger.error(f"Location forecast failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_location_alerts_impl(query: str, language: str = "en-us") -> dict:
    """Implementation function for get_location_alerts"""
    try:
        # Search for location
        locations = await weather_client.search_locations(query, language)
        if not locations:
            return {"success": False, "error": f"No locations found for '{query}'"}
        
        # Get alerts for first location
        location_key = locations[0]["Key"]
        alerts = await weather_client.get_weather_alerts(location_key)
        
        return {
            "success": True,
            "location": locations[0],
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
            ],
            "count": len(alerts)
        }
    except Exception as e:
        logger.error(f"Location alerts failed: {e}")
        return {"success": False, "error": str(e)}


@mcp.tool()
async def search_locations(query: LocationQuery) -> dict:
    """Search for weather locations by name or ZIP code"""
    return await _search_locations_impl(query.query, query.language)


@mcp.tool()
async def get_current_weather(location: LocationKey) -> dict:
    """Get current weather conditions for a location"""
    return await _get_current_weather_impl(location.location_key, location.details)


@mcp.tool()
async def get_5day_forecast(forecast: ForecastQuery) -> dict:
    """Get 5-day weather forecast for a location"""
    return await _get_5day_forecast_impl(forecast.location_key, forecast.metric)


@mcp.tool()
async def get_weather_alerts(location: LocationKey) -> dict:
    """Get weather alerts for a location"""
    return await _get_weather_alerts_impl(location.location_key)


@mcp.tool()
async def get_location_weather(query: LocationQuery) -> dict:
    """Get current weather by searching for a location first"""
    return await _get_location_weather_impl(query.query, query.language)


@mcp.tool()
async def get_location_forecast(query: LocationQuery) -> dict:
    """Get 5-day forecast by searching for a location first"""
    return await _get_location_forecast_impl(query.query, query.language)


@mcp.tool()
async def get_location_alerts(query: LocationQuery) -> dict:
    """Get weather alerts by searching for a location first"""
    return await _get_location_alerts_impl(query.query, query.language)


async def test_nws_api():
    """Test the NWS API connection"""
    try:
        logger.info("Testing National Weather Service API connection...")
        
        # Test location search
        logger.info("Testing location search...")
        locations = await weather_client.search_locations("10001")  # NYC ZIP
        if locations:
            logger.info(f"✓ Location search successful: {locations[0]['LocalizedName']}")
            location_key = locations[0]["Key"]
            
            # Test current weather
            logger.info("Testing current weather...")
            weather = await weather_client.get_current_weather(location_key)
            logger.info(f"✓ Current weather: {weather.temperature}°{weather.temperature_unit}, {weather.weather_text}")
            
            # Test forecast
            logger.info("Testing 5-day forecast...")
            forecasts = await weather_client.get_5day_forecast(location_key)
            logger.info(f"✓ 5-day forecast: {len(forecasts)} days retrieved")
            
            # Test alerts
            logger.info("Testing weather alerts...")
            alerts = await weather_client.get_weather_alerts(location_key)
            logger.info(f"✓ Weather alerts: {len(alerts)} active alerts")
            
            logger.info("🎉 All NWS API tests passed!")
        else:
            logger.error("✗ Location search failed")
            
    except Exception as e:
        logger.error(f"✗ NWS API test failed: {e}")


@asynccontextmanager
async def get_weather_client():
    """Get weather client context manager"""
    global weather_client
    try:
        weather_client = NationalWeatherServiceClient()
        yield weather_client
    finally:
        if weather_client:
            await weather_client.close()


async def main():
    """Main application entry point"""
    global weather_client
    
    # Load configuration
    config = Config()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]
        
        if mode == "test":
            # Test NWS API connection
            async with get_weather_client() as client:
                await test_nws_api()
            
        elif mode == "sse":
            # Run SSE server
            logger.info("Starting Weather MCP SSE Server (National Weather Service)")
            
            async with get_weather_client() as client:
                sse_app = WeatherSSEApp(config, client)
                app = sse_app.get_app()
                
                # Use uvicorn server directly to avoid asyncio.run() conflict
                import uvicorn
                server_config = uvicorn.Config(app, host="0.0.0.0", port=8000)
                server = uvicorn.Server(server_config)
                await server.serve()
        
        elif mode == "mcp":
            # Run MCP server
            logger.info("Starting Weather MCP Server (National Weather Service)")
            
            async with get_weather_client() as client:
                # Run the MCP server
                await mcp.run(transport="stdio")
        
        else:
            logger.error(f"Unknown mode: {mode}")
            logger.info("Usage: python main.py [test|sse|mcp]")
            sys.exit(1)
    
    else:
        # Default to MCP mode
        logger.info("Starting Weather MCP Server (National Weather Service)")
        
        async with get_weather_client() as client:
            await mcp.run(transport="stdio")


if __name__ == "__main__":
    asyncio.run(main()) 