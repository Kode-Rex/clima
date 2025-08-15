"""
Forecast service for handling weather forecast operations
"""

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from ..nws import NationalWeatherServiceClient


class ForecastService:
    """Service for weather forecast operations"""

    def __init__(self, weather_client: "NationalWeatherServiceClient"):
        self.weather_client = weather_client

    async def get_5day_forecast(self, location_key: str, metric: bool = True) -> dict:
        """Get 5-day weather forecast for a location"""
        try:
            forecasts = await self.weather_client.get_5day_forecast(
                location_key, metric
            )
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
                        "night_precipitation_probability": f.night_precipitation_probability,
                    }
                    for f in forecasts
                ],
                "count": len(forecasts),
            }
        except Exception as e:
            logger.error(f"5-day forecast failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_extended_forecast(
        self, location_key: str, days: int = 7, metric: bool = True
    ) -> dict:
        """Get extended weather forecast for a location (up to 7 days)"""
        try:
            forecasts = await self.weather_client.get_daily_forecast(
                location_key, days, metric
            )
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
                        "night_precipitation_probability": f.night_precipitation_probability,
                    }
                    for f in forecasts
                ],
                "count": len(forecasts),
                "days": days,
            }
        except Exception as e:
            logger.error(f"Extended forecast failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_hourly_forecast(
        self, location_key: str, hours: int = 168, metric: bool = True
    ) -> dict:
        """Get hourly weather forecast for a location (up to 168 hours/7 days)"""
        try:
            forecasts = await self.weather_client.get_hourly_forecast(
                location_key, hours, metric
            )
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
                        "is_daytime": f.is_daytime,
                    }
                    for f in forecasts
                ],
                "count": len(forecasts),
                "hours": hours,
            }
        except Exception as e:
            logger.error(f"Hourly forecast failed: {e}")
            return {"success": False, "error": str(e)}
