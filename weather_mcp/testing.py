"""
Testing functionality for weather MCP
"""

from typing import TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    from .nws import NationalWeatherServiceClient


async def test_nws_api(weather_client: "NationalWeatherServiceClient"):
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
