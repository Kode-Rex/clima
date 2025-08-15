"""
Alert service for handling weather alert operations
"""

from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from ..nws import NationalWeatherServiceClient


class AlertService:
    """Service for weather alert operations"""

    def __init__(self, weather_client: "NationalWeatherServiceClient"):
        self.weather_client = weather_client

    async def get_weather_alerts(self, location_key: str) -> dict:
        """Get weather alerts for a location"""
        try:
            alerts = await self.weather_client.get_weather_alerts(location_key)
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
                        "end_time": (
                            alert.end_time.isoformat() if alert.end_time else None
                        ),
                        "areas": alert.areas,
                    }
                    for alert in alerts
                ],
                "count": len(alerts),
            }
        except Exception as e:
            logger.error(f"Weather alerts failed: {e}")
            return {"success": False, "error": str(e)}
