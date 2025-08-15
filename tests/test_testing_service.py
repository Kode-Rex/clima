"""
Tests for WeatherTestingService
"""

from unittest.mock import AsyncMock

import pytest

from weather_mcp.services.testing_service import WeatherTestingService


class TestWeatherTestingService:
    """Test class for WeatherTestingService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_nws_api_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful NWS API test"""
        # Setup mock responses
        mock_weather_client.search_locations.return_value = (
            sample_location_search_response
        )

        testing_service = WeatherTestingService(mock_weather_client)
        result = await testing_service.test_nws_api()

        assert result["success"] is True
        assert "location_search" in result
        assert result["location_search"]["success"] is True

        # Verify the service called the expected methods
        mock_weather_client.search_locations.assert_called_once_with("10001")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_nws_api_location_search_failure(self, mock_weather_client):
        """Test NWS API test with location search failure"""
        # Mock location search to return empty list
        mock_weather_client.search_locations.return_value = []

        testing_service = WeatherTestingService(mock_weather_client)
        result = await testing_service.test_nws_api()

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_nws_api_exception_handling(self, mock_weather_client):
        """Test NWS API test with exception"""
        # Mock location search to raise an exception
        mock_weather_client.search_locations.side_effect = Exception(
            "API Connection Error"
        )

        testing_service = WeatherTestingService(mock_weather_client)
        result = await testing_service.test_nws_api()

        assert result["success"] is False
        assert "API Connection Error" in result["error"]

    @pytest.mark.unit
    def test_testing_service_initialization(self, mock_weather_client):
        """Test WeatherTestingService initialization"""
        testing_service = WeatherTestingService(mock_weather_client)

        assert testing_service.weather_client == mock_weather_client
        assert hasattr(testing_service, "test_nws_api")
