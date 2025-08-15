"""
Weather service for handling current weather operations
"""

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from ..nws import NationalWeatherServiceClient


class WeatherService:
    """Service for current weather operations"""

    def __init__(self, weather_client: "NationalWeatherServiceClient"):
        self.weather_client = weather_client

    async def get_current_weather(
        self, location_key: str, details: bool = True
    ) -> dict:
        """Get current weather conditions for a location"""
        try:
            weather = await self.weather_client.get_current_weather(
                location_key, details
            )
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
                    "local_time": weather.local_time.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Current weather failed: {e}")
            return {"success": False, "error": str(e)}
