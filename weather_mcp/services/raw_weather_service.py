"""
Raw weather service for handling detailed meteorological data operations
"""

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from ..nws import NationalWeatherServiceClient


class RawWeatherService:
    """Service for detailed raw meteorological data operations"""

    def __init__(self, weather_client: "NationalWeatherServiceClient"):
        self.weather_client = weather_client

    async def get_detailed_grid_data(
        self, location_key: str, metric: bool = True
    ) -> dict:
        """Get detailed grid forecast data with comprehensive weather parameters"""
        try:
            grid_data = await self.weather_client.get_detailed_grid_data(
                location_key, metric
            )
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
                        "precipitation_unit": d.precipitation_unit,
                    }
                    for d in grid_data
                ],
                "count": len(grid_data),
            }
        except Exception as e:
            logger.error(f"Detailed grid data failed: {e}")
            return {"success": False, "error": str(e)}
