"""
Tests for ForecastService
"""

import pytest

from weather_mcp.services.forecast_service import ForecastService


class TestForecastService:
    """Test class for ForecastService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_5day_forecast_success(self, mock_weather_client):
        """Test successful 5-day forecast retrieval"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_5day_forecast("40.7128,-74.0060", True)

        assert result["success"] is True
        assert result["count"] == 1
        forecast_data = result["forecasts"][0]
        assert "2024-01-15" in forecast_data["date"]  # Allow for timezone formatting
        assert forecast_data["min_temperature"] == -2.0
        assert forecast_data["max_temperature"] == 5.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_5day_forecast_default_metric(self, mock_weather_client):
        """Test 5-day forecast with default metric parameter"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_5day_forecast("40.7128,-74.0060")

        assert result["success"] is True
        assert result["count"] == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_5day_forecast_error(self, mock_weather_client):
        """Test get_5day_forecast error handling"""
        mock_weather_client.get_5day_forecast.side_effect = Exception(
            "Forecast API Error"
        )

        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_5day_forecast("40.7128,-74.0060")

        assert result["success"] is False
        assert "Forecast API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_extended_forecast_success(self, mock_weather_client):
        """Test successful extended forecast retrieval"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_extended_forecast(
            "40.7128,-74.0060", 7, True
        )

        assert result["success"] is True
        assert result["days"] == 7
        assert result["count"] >= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_extended_forecast_default_params(self, mock_weather_client):
        """Test extended forecast with default parameters"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_extended_forecast("40.7128,-74.0060")

        assert result["success"] is True
        assert result["days"] == 7  # Default value

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_extended_forecast_error(self, mock_weather_client):
        """Test get_extended_forecast error handling"""
        mock_weather_client.get_daily_forecast.side_effect = Exception(
            "Extended Forecast API Error"
        )

        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_extended_forecast("40.7128,-74.0060")

        assert result["success"] is False
        assert "Extended Forecast API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_success(self, mock_weather_client):
        """Test successful hourly forecast retrieval"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_hourly_forecast(
            "40.7128,-74.0060", 24, True
        )

        assert result["success"] is True
        assert result["hours"] == 24
        assert result["count"] >= 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_default_params(self, mock_weather_client):
        """Test hourly forecast with default parameters"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_hourly_forecast("40.7128,-74.0060")

        assert result["success"] is True
        assert result["hours"] == 168  # Default value

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_error(self, mock_weather_client):
        """Test get_hourly_forecast error handling"""
        mock_weather_client.get_hourly_forecast.side_effect = Exception(
            "Hourly Forecast API Error"
        )

        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_hourly_forecast("40.7128,-74.0060")

        assert result["success"] is False
        assert "Hourly Forecast API Error" in result["error"]
