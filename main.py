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


class ExtendedForecastQuery(BaseModel):
    """Extended forecast query parameters"""
    location_key: str = Field(..., description="Location identifier (lat,lon format)")
    days: int = Field(7, description="Number of days for forecast (up to 7)")
    metric: bool = Field(True, description="Use metric units (Celsius)")


class HourlyForecastQuery(BaseModel):
    """Hourly forecast query parameters"""
    location_key: str = Field(..., description="Location identifier (lat,lon format)")
    hours: int = Field(168, description="Number of hours for forecast (up to 168 hours/7 days)")
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


async def _get_extended_forecast_impl(location_key: str, days: int = 7, metric: bool = True) -> dict:
    """Implementation function for get_extended_forecast"""
    try:
        forecasts = await weather_client.get_daily_forecast(location_key, days, metric)
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
            "count": len(forecasts),
            "days": days
        }
    except Exception as e:
        logger.error(f"Extended forecast failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_hourly_forecast_impl(location_key: str, hours: int = 168, metric: bool = True) -> dict:
    """Implementation function for get_hourly_forecast"""
    try:
        forecasts = await weather_client.get_hourly_forecast(location_key, hours, metric)
        return {
            "success": True,
            "forecasts": [
                {
                    "timestamp": f.timestamp.isoformat(),
                    "temperature": f.temperature,
                    "temperature_unit": f.temperature_unit,
                    "humidity": f.humidity,
                    "wind_speed": f.wind_speed,
                    "wind_direction": f.wind_direction,
                    "wind_gust": f.wind_gust,
                    "pressure": f.pressure,
                    "visibility": f.visibility,
                    "precipitation_probability": f.precipitation_probability,
                    "precipitation_amount": f.precipitation_amount,
                    "weather_text": f.weather_text,
                    "weather_icon": f.weather_icon,
                    "sky_cover": f.sky_cover,
                    "dewpoint": f.dewpoint,
                    "apparent_temperature": f.apparent_temperature,
                    "uv_index": f.uv_index,
                    "is_daytime": f.is_daytime
                }
                for f in forecasts
            ],
            "count": len(forecasts),
            "hours": hours
        }
    except Exception as e:
        logger.error(f"Hourly forecast failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_detailed_grid_data_impl(location_key: str, metric: bool = True) -> dict:
    """Implementation function for get_detailed_grid_data"""
    try:
        grid_data = await weather_client.get_detailed_grid_data(location_key, metric)
        return {
            "success": True,
            "grid_data": [
                {
                    "timestamp": d.timestamp.isoformat(),
                    "temperature": d.temperature,
                    "dewpoint": d.dewpoint,
                    "max_temperature": d.max_temperature,
                    "min_temperature": d.min_temperature,
                    "relative_humidity": d.relative_humidity,
                    "apparent_temperature": d.apparent_temperature,
                    "heat_index": d.heat_index,
                    "wind_chill": d.wind_chill,
                    "sky_cover": d.sky_cover,
                    "wind_direction": d.wind_direction,
                    "wind_speed": d.wind_speed,
                    "wind_gust": d.wind_gust,
                    "weather_conditions": d.weather_conditions,
                    "probability_of_precipitation": d.probability_of_precipitation,
                    "quantitative_precipitation": d.quantitative_precipitation,
                    "ice_accumulation": d.ice_accumulation,
                    "snowfall_amount": d.snowfall_amount,
                    "snow_level": d.snow_level,
                    "ceiling_height": d.ceiling_height,
                    "visibility": d.visibility,
                    "pressure": d.pressure,
                    "temperature_unit": d.temperature_unit,
                    "distance_unit": d.distance_unit,
                    "speed_unit": d.speed_unit,
                    "precipitation_unit": d.precipitation_unit
                }
                for d in grid_data
            ],
            "count": len(grid_data)
        }
    except Exception as e:
        logger.error(f"Detailed grid data failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_location_extended_forecast_impl(query: str, days: int = 7, language: str = "en-us") -> dict:
    """Implementation function for get_location_extended_forecast"""
    try:
        # Search for location
        locations = await weather_client.search_locations(query, language)
        if not locations:
            return {"success": False, "error": f"No locations found for '{query}'"}
        
        # Get extended forecast for first location
        location_key = locations[0]["Key"]
        forecasts = await weather_client.get_daily_forecast(location_key, days, True)
        
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
            "count": len(forecasts),
            "days": days
        }
    except Exception as e:
        logger.error(f"Location extended forecast failed: {e}")
        return {"success": False, "error": str(e)}


async def _get_location_hourly_forecast_impl(query: str, hours: int = 168, language: str = "en-us") -> dict:
    """Implementation function for get_location_hourly_forecast"""
    try:
        # Search for location
        locations = await weather_client.search_locations(query, language)
        if not locations:
            return {"success": False, "error": f"No locations found for '{query}'"}
        
        # Get hourly forecast for first location
        location_key = locations[0]["Key"]
        forecasts = await weather_client.get_hourly_forecast(location_key, hours, True)
        
        return {
            "success": True,
            "location": locations[0],
            "forecasts": [
                {
                    "timestamp": f.timestamp.isoformat(),
                    "temperature": f.temperature,
                    "temperature_unit": f.temperature_unit,
                    "humidity": f.humidity,
                    "wind_speed": f.wind_speed,
                    "wind_direction": f.wind_direction,
                    "wind_gust": f.wind_gust,
                    "pressure": f.pressure,
                    "visibility": f.visibility,
                    "precipitation_probability": f.precipitation_probability,
                    "precipitation_amount": f.precipitation_amount,
                    "weather_text": f.weather_text,
                    "weather_icon": f.weather_icon,
                    "sky_cover": f.sky_cover,
                    "dewpoint": f.dewpoint,
                    "apparent_temperature": f.apparent_temperature,
                    "uv_index": f.uv_index,
                    "is_daytime": f.is_daytime
                }
                for f in forecasts
            ],
            "count": len(forecasts),
            "hours": hours
        }
    except Exception as e:
        logger.error(f"Location hourly forecast failed: {e}")
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


@mcp.tool()
async def get_7day_forecast(forecast: ForecastQuery) -> dict:
    """Get 7-day weather forecast for a location"""
    return await _get_extended_forecast_impl(forecast.location_key, days=7, metric=forecast.metric)


@mcp.tool()
async def get_extended_forecast(forecast: ExtendedForecastQuery) -> dict:
    """Get extended weather forecast for a location (up to 7 days)"""
    return await _get_extended_forecast_impl(forecast.location_key, forecast.days, forecast.metric)


@mcp.tool()
async def get_hourly_forecast(forecast: HourlyForecastQuery) -> dict:
    """Get hourly weather forecast for a location (up to 168 hours/7 days)"""
    return await _get_hourly_forecast_impl(forecast.location_key, forecast.hours, forecast.metric)


@mcp.tool()
async def get_detailed_grid_data(location: LocationKey) -> dict:
    """Get detailed grid forecast data with comprehensive weather parameters"""
    return await _get_detailed_grid_data_impl(location.location_key, metric=True)


@mcp.tool()
async def get_location_extended_forecast(query: LocationQuery) -> dict:
    """Get 7-day forecast by searching for a location first"""
    return await _get_location_extended_forecast_impl(query.query, days=7, language=query.language)


@mcp.tool()
async def get_location_hourly_forecast(query: LocationQuery) -> dict:
    """Get hourly forecast by searching for a location first"""
    return await _get_location_hourly_forecast_impl(query.query, hours=168, language=query.language)


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
            
            # Test 7-day forecast
            logger.info("Testing 7-day forecast...")
            extended_forecasts = await weather_client.get_7day_forecast(location_key)
            logger.info(f"✓ 7-day forecast: {len(extended_forecasts)} days retrieved")
            
            # Test hourly forecast
            logger.info("Testing hourly forecast...")
            hourly_forecasts = await weather_client.get_hourly_forecast(location_key, hours=24)
            logger.info(f"✓ Hourly forecast: {len(hourly_forecasts)} hours retrieved")
            
            # Test detailed grid data
            logger.info("Testing detailed grid data...")
            try:
                grid_data = await weather_client.get_detailed_grid_data(location_key)
                logger.info(f"✓ Detailed grid data: {len(grid_data)} data points retrieved")
            except Exception as e:
                logger.warning(f"⚠ Detailed grid data test failed (may not be available): {e}")
            
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
                # For MCP mode, we need to exit this coroutine and let FastMCP handle the event loop
                return
        
        else:
            logger.error(f"Unknown mode: {mode}")
            logger.info("Usage: python main.py [test|sse|mcp]")
            sys.exit(1)
    
    else:
        # Default to MCP mode
        logger.info("Starting Weather MCP Server (National Weather Service)")
        
        async with get_weather_client() as client:
            # For MCP mode, we need to exit this coroutine and let FastMCP handle the event loop
            return


if __name__ == "__main__":
    # Handle different modes with appropriate event loop management
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] in ["test", "sse"]:
        # For test and sse modes, use normal asyncio.run()
        asyncio.run(main())
    else:
        # For MCP mode, let FastMCP handle the event loop entirely
        asyncio.run(main())  # Initialize dependencies
        
        # Now run MCP server with its own event loop
        from weather_mcp.nws import NationalWeatherServiceClient
        
        async def setup_mcp():
            global weather_client
            weather_client = NationalWeatherServiceClient()
            
        asyncio.run(setup_mcp())
        mcp.run(transport="stdio") 