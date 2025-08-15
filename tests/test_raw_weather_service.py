"""
Tests for RawWeatherService
"""

import pytest

from weather_mcp.services.raw_weather_service import RawWeatherService


class TestRawWeatherService:
    """Test class for RawWeatherService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_success(self, mock_weather_client):
        """Test successful detailed raw weather data retrieval"""
        raw_weather_service = RawWeatherService(mock_weather_client)
        result = await raw_weather_service.get_detailed_grid_data(
            "40.7128,-74.0060", True
        )

        assert result["success"] is True
        assert result["count"] >= 1
        grid_data = result["grid_data"][0]
        assert "timestamp" in grid_data
        assert "temperature" in grid_data
        assert "dewpoint" in grid_data
        assert "relative_humidity" in grid_data

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_default_params(self, mock_weather_client):
        """Test detailed grid data with default parameters"""
        raw_weather_service = RawWeatherService(mock_weather_client)
        result = await raw_weather_service.get_detailed_grid_data("40.7128,-74.0060")

        assert result["success"] is True
        mock_weather_client.get_detailed_grid_data.assert_called_once_with(
            "40.7128,-74.0060", True
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_error(self, mock_weather_client):
        """Test get_detailed_grid_data error handling"""
        mock_weather_client.get_detailed_grid_data.side_effect = Exception(
            "Raw Weather Data API Error"
        )

        raw_weather_service = RawWeatherService(mock_weather_client)
        result = await raw_weather_service.get_detailed_grid_data("40.7128,-74.0060")

        assert result["success"] is False
        assert "Raw Weather Data API Error" in result["error"]
