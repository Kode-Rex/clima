"""
Location service for handling location searches and operations
"""

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from ..nws import NationalWeatherServiceClient


class LocationService:
    """Service for location-related operations"""

    def __init__(self, weather_client: "NationalWeatherServiceClient"):
        self.weather_client = weather_client

    async def search_locations(self, query: str, language: str = "en-us") -> dict:
        """Search for weather locations by name or ZIP code"""
        try:
            results = await self.weather_client.search_locations(query, language)
            return {"success": True, "locations": results, "count": len(results)}
        except Exception as e:
            logger.error(f"Location search failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_location_weather(self, query: str, language: str = "en-us") -> dict:
        """Get current weather by searching for a location first"""
        try:
            from .weather_service import WeatherService

            # Search for location
            locations = await self.weather_client.search_locations(query, language)
            if not locations:
                return {"success": False, "error": f"No locations found for '{query}'"}

            # Get weather for first location
            location_key = locations[0]["Key"]
            weather_service = WeatherService(self.weather_client)
            weather_result = await weather_service.get_current_weather(
                location_key, True
            )

            if not weather_result["success"]:
                return weather_result

            return {
                "success": True,
                "location": locations[0],
                "weather": weather_result["weather"],
            }
        except Exception as e:
            logger.error(f"Location weather failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_location_forecast(self, query: str, language: str = "en-us") -> dict:
        """Get 5-day forecast by searching for a location first"""
        try:
            from .forecast_service import ForecastService

            # Search for location
            locations = await self.weather_client.search_locations(query, language)
            if not locations:
                return {"success": False, "error": f"No locations found for '{query}'"}

            # Get forecast for first location
            location_key = locations[0]["Key"]
            forecast_service = ForecastService(self.weather_client)
            forecast_result = await forecast_service.get_5day_forecast(
                location_key, True
            )

            if not forecast_result["success"]:
                return forecast_result

            return {
                "success": True,
                "location": locations[0],
                "forecasts": forecast_result["forecasts"],
                "count": forecast_result["count"],
            }
        except Exception as e:
            logger.error(f"Location forecast failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_location_alerts(self, query: str, language: str = "en-us") -> dict:
        """Get weather alerts by searching for a location first"""
        try:
            from .alert_service import AlertService

            # Search for location
            locations = await self.weather_client.search_locations(query, language)
            if not locations:
                return {"success": False, "error": f"No locations found for '{query}'"}

            # Get alerts for first location
            location_key = locations[0]["Key"]
            alert_service = AlertService(self.weather_client)
            alert_result = await alert_service.get_weather_alerts(location_key)

            if not alert_result["success"]:
                return alert_result

            return {
                "success": True,
                "location": locations[0],
                "alerts": alert_result["alerts"],
                "count": alert_result["count"],
            }
        except Exception as e:
            logger.error(f"Location alerts failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_location_extended_forecast(
        self, query: str, days: int = 7, language: str = "en-us"
    ) -> dict:
        """Get extended forecast by searching for a location first"""
        try:
            from .forecast_service import ForecastService

            # Search for location
            locations = await self.weather_client.search_locations(query, language)
            if not locations:
                return {"success": False, "error": f"No locations found for '{query}'"}

            # Get extended forecast for first location
            location_key = locations[0]["Key"]
            forecast_service = ForecastService(self.weather_client)
            forecast_result = await forecast_service.get_extended_forecast(
                location_key, days, True
            )

            if not forecast_result["success"]:
                return forecast_result

            return {
                "success": True,
                "location": locations[0],
                "forecasts": forecast_result["forecasts"],
                "count": forecast_result["count"],
                "days": days,
            }
        except Exception as e:
            logger.error(f"Location extended forecast failed: {e}")
            return {"success": False, "error": str(e)}

    async def get_location_hourly_forecast(
        self, query: str, hours: int = 168, language: str = "en-us"
    ) -> dict:
        """Get hourly forecast by searching for a location first"""
        try:
            from .forecast_service import ForecastService

            # Search for location
            locations = await self.weather_client.search_locations(query, language)
            if not locations:
                return {"success": False, "error": f"No locations found for '{query}'"}

            # Get hourly forecast for first location
            location_key = locations[0]["Key"]
            forecast_service = ForecastService(self.weather_client)
            forecast_result = await forecast_service.get_hourly_forecast(
                location_key, hours, True
            )

            if not forecast_result["success"]:
                return forecast_result

            return {
                "success": True,
                "location": locations[0],
                "forecasts": forecast_result["forecasts"],
                "count": forecast_result["count"],
                "hours": hours,
            }
        except Exception as e:
            logger.error(f"Location hourly forecast failed: {e}")
            return {"success": False, "error": str(e)}
