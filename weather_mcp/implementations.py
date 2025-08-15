"""
Implementation functions for weather MCP tools
"""

from typing import TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from .nws import NationalWeatherServiceClient


async def search_locations_impl(
    weather_client: "NationalWeatherServiceClient", 
    query: str, 
    language: str = "en-us"
) -> dict:
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


async def get_current_weather_impl(
    weather_client: "NationalWeatherServiceClient",
    location_key: str, 
    details: bool = True
) -> dict:
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


async def get_5day_forecast_impl(
    weather_client: "NationalWeatherServiceClient",
    location_key: str, 
    metric: bool = True
) -> dict:
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


async def get_weather_alerts_impl(
    weather_client: "NationalWeatherServiceClient",
    location_key: str
) -> dict:
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


async def get_location_weather_impl(
    weather_client: "NationalWeatherServiceClient",
    query: str, 
    language: str = "en-us"
) -> dict:
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


async def get_location_forecast_impl(
    weather_client: "NationalWeatherServiceClient",
    query: str, 
    language: str = "en-us"
) -> dict:
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


async def get_location_alerts_impl(
    weather_client: "NationalWeatherServiceClient",
    query: str, 
    language: str = "en-us"
) -> dict:
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


async def get_extended_forecast_impl(
    weather_client: "NationalWeatherServiceClient",
    location_key: str, 
    days: int = 7, 
    metric: bool = True
) -> dict:
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


async def get_hourly_forecast_impl(
    weather_client: "NationalWeatherServiceClient",
    location_key: str, 
    hours: int = 168, 
    metric: bool = True
) -> dict:
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


async def get_detailed_grid_data_impl(
    weather_client: "NationalWeatherServiceClient",
    location_key: str, 
    metric: bool = True
) -> dict:
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


async def get_location_extended_forecast_impl(
    weather_client: "NationalWeatherServiceClient",
    query: str, 
    days: int = 7, 
    language: str = "en-us"
) -> dict:
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


async def get_location_hourly_forecast_impl(
    weather_client: "NationalWeatherServiceClient",
    query: str, 
    hours: int = 168, 
    language: str = "en-us"
) -> dict:
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
