"""
Tests for AlertService
"""

import pytest

from weather_mcp.services.alert_service import AlertService


class TestAlertService:
    """Test class for AlertService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_alerts_success(self, mock_weather_client):
        """Test successful weather alerts retrieval"""
        alert_service = AlertService(mock_weather_client)
        result = await alert_service.get_weather_alerts("40.7128,-74.0060")

        assert result["success"] is True
        assert result["count"] >= 1
        alert = result["alerts"][0]
        assert "alert_id" in alert
        assert "title" in alert
        assert "severity" in alert

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_alerts_error(self, mock_weather_client):
        """Test get_weather_alerts error handling"""
        mock_weather_client.get_weather_alerts.side_effect = Exception(
            "Alerts API Error"
        )

        alert_service = AlertService(mock_weather_client)
        result = await alert_service.get_weather_alerts("40.7128,-74.0060")

        assert result["success"] is False
        assert "Alerts API Error" in result["error"]
