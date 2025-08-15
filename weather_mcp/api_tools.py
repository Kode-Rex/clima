"""
Weather API tools for FastMCP with SSE support
Provides HTTP-accessible weather tools for API integration
"""

from typing import TYPE_CHECKING

from fastmcp import FastMCP

if TYPE_CHECKING:
    from .nws import NationalWeatherServiceClient


def setup_weather_tools(mcp: FastMCP, weather_client: "NationalWeatherServiceClient"):
    """Setup weather tools for HTTP/SSE API access"""

    @mcp.tool()
    async def get_weather(zip_code: str) -> dict:
        """Get current weather for a ZIP code"""
        try:
            # Search for location
            locations = await weather_client.search_locations(zip_code)
            if not locations:
                return {"error": f"No location found for ZIP code: {zip_code}"}

            location_key = locations[0]["Key"]

            # Get current weather
            weather = await weather_client.get_current_weather(location_key)

            return {
                "location": locations[0]["LocalizedName"],
                "temperature": weather.temperature,
                "temperature_unit": weather.temperature_unit,
                "weather_text": weather.weather_text,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
                "wind_direction": weather.wind_direction,
                "pressure": weather.pressure,
                "visibility": weather.visibility,
                "uv_index": weather.uv_index,
                "precipitation": weather.precipitation,
            }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    async def get_forecast(zip_code: str, days: int = 5) -> dict:
        """Get weather forecast for a ZIP code"""
        try:
            # Search for location
            locations = await weather_client.search_locations(zip_code)
            if not locations:
                return {"error": f"No location found for ZIP code: {zip_code}"}

            location_key = locations[0]["Key"]

            # Get forecast
            forecast = await weather_client.get_5day_forecast(location_key)

            # Format forecast data
            daily_forecasts = []
            for day in forecast[:days]:
                daily_forecasts.append(
                    {
                        "date": day.date.isoformat(),
                        "min_temperature": day.min_temperature,
                        "max_temperature": day.max_temperature,
                        "temperature_unit": day.temperature_unit,
                        "day_weather_text": day.day_weather_text,
                        "day_weather_icon": day.day_weather_icon,
                        "day_precipitation_probability": day.day_precipitation_probability,
                        "night_weather_text": day.night_weather_text,
                        "night_weather_icon": day.night_weather_icon,
                        "night_precipitation_probability": day.night_precipitation_probability,
                    }
                )

            return {
                "location": locations[0]["LocalizedName"],
                "forecast": daily_forecasts,
            }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    async def get_alerts(zip_code: str) -> dict:
        """Get weather alerts for a ZIP code"""
        try:
            # Search for location
            locations = await weather_client.search_locations(zip_code)
            if not locations:
                return {"error": f"No location found for ZIP code: {zip_code}"}

            location_key = locations[0]["Key"]

            # Get alerts
            alerts = await weather_client.get_weather_alerts(location_key)

            # Format alerts
            alert_list = []
            for alert in alerts:
                alert_list.append(
                    {
                        "alert_id": alert.alert_id,
                        "title": alert.title,
                        "description": alert.description,
                        "severity": alert.severity,
                        "category": alert.category,
                        "start_time": alert.start_time.isoformat(),
                        "end_time": (
                            alert.end_time.isoformat() if alert.end_time else None
                        ),
                        "areas": alert.areas,
                    }
                )

            return {
                "location": locations[0]["LocalizedName"],
                "alerts": alert_list,
                "count": len(alert_list),
            }
        except Exception as e:
            return {"error": str(e)}

    @mcp.tool()
    async def search_locations(query: str) -> dict:
        """Search for locations by name or ZIP code"""
        try:
            locations = await weather_client.search_locations(query)

            # Format locations
            location_list = []
            for location in locations:
                location_list.append(
                    {
                        "key": location.get("Key", ""),
                        "name": location.get("LocalizedName", ""),
                        "country": location.get("Country", {}).get("LocalizedName", ""),
                        "region": location.get("AdministrativeArea", {}).get(
                            "LocalizedName", ""
                        ),
                        "postal_code": location.get("PrimaryPostalCode", ""),
                    }
                )

            return {
                "locations": location_list,
                "count": len(location_list),
            }
        except Exception as e:
            return {"error": str(e)}
