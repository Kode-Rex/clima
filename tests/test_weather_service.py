"""
Tests for WeatherService
"""

import pytest

from weather_mcp.services.weather_service import WeatherService


class TestWeatherService:
    """Test class for WeatherService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, mock_weather_client):
        """Test successful current weather retrieval"""
        weather_service = WeatherService(mock_weather_client)
        result = await weather_service.get_current_weather("40.7128,-74.0060", True)

        assert result["success"] is True
        weather = result["weather"]
        assert weather["temperature"] == 5.0
        assert weather["temperature_unit"] == "C"
        assert weather["humidity"] == 65
        assert weather["wind_speed"] == 15.0
        assert weather["wind_direction"] == "SW"
        assert weather["weather_text"] == "Partly Cloudy"
        assert weather["uv_index"] == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_default_details(self, mock_weather_client):
        """Test current weather with default details parameter"""
        weather_service = WeatherService(mock_weather_client)
        result = await weather_service.get_current_weather("40.7128,-74.0060")

        assert result["success"] is True
        weather = result["weather"]
        assert weather["temperature"] == 5.0
        assert weather["temperature_unit"] == "C"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_error(self, mock_weather_client):
        """Test get_current_weather error handling"""
        mock_weather_client.get_current_weather.side_effect = Exception(
            "Weather API Error"
        )

        weather_service = WeatherService(mock_weather_client)
        result = await weather_service.get_current_weather("40.7128,-74.0060")

        assert result["success"] is False
        assert "Weather API Error" in result["error"]
