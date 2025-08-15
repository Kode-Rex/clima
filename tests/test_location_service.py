"""
Tests for LocationService
"""

import pytest

from weather_mcp.services.location_service import LocationService


class TestLocationService:
    """Test class for LocationService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_locations_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location search"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.search_locations("New York", "en-us")

        assert result["success"] is True
        assert result["locations"] == sample_location_search_response
        assert result["count"] == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_locations_without_language(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test location search with default language"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.search_locations("Paris")

        assert result["success"] is True
        assert result["locations"] == sample_location_search_response
        mock_weather_client.search_locations.assert_called_once_with("Paris", "en-us")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_locations_error(self, mock_weather_client):
        """Test search_locations error handling"""
        mock_weather_client.search_locations.side_effect = Exception("API Error")

        location_service = LocationService(mock_weather_client)
        result = await location_service.search_locations("New York")

        assert result["success"] is False
        assert "API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_weather_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location weather retrieval"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_weather("New York", "en-us")

        assert result["success"] is True
        assert "location" in result
        assert "weather" in result
        assert result["location"] == sample_location_search_response[0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_weather_no_locations(self, mock_weather_client):
        """Test location weather with no locations found"""
        mock_weather_client.search_locations.return_value = []

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_weather("NonexistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_weather_error(self, mock_weather_client):
        """Test location weather error handling"""
        mock_weather_client.search_locations.side_effect = Exception(
            "Location API Error"
        )

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_weather("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_forecast_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location forecast retrieval"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_forecast("New York", "en-us")

        assert result["success"] is True
        assert "location" in result
        assert "forecasts" in result
        assert result["location"] == sample_location_search_response[0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_forecast_no_locations(self, mock_weather_client):
        """Test location forecast with no locations found"""
        mock_weather_client.search_locations.return_value = []

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_forecast("NonexistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_forecast_error(self, mock_weather_client):
        """Test location forecast error handling"""
        mock_weather_client.search_locations.side_effect = Exception(
            "Location API Error"
        )

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_forecast("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_alerts_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location alerts retrieval"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_alerts("New York", "en-us")

        assert result["success"] is True
        assert "location" in result
        assert "alerts" in result
        assert result["location"] == sample_location_search_response[0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_alerts_no_locations(self, mock_weather_client):
        """Test location alerts with no locations found"""
        mock_weather_client.search_locations.return_value = []

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_alerts("NonexistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_alerts_error(self, mock_weather_client):
        """Test location alerts error handling"""
        mock_weather_client.search_locations.side_effect = Exception(
            "Location API Error"
        )

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_alerts("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location extended forecast retrieval"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_extended_forecast(
            "New York", 7, "en-us"
        )

        assert result["success"] is True
        assert "location" in result
        assert "forecasts" in result
        assert result["days"] == 7

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_no_locations(
        self, mock_weather_client
    ):
        """Test location extended forecast with no locations found"""
        mock_weather_client.search_locations.return_value = []

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_extended_forecast(
            "NonexistentPlace"
        )

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_error(self, mock_weather_client):
        """Test location extended forecast error handling"""
        mock_weather_client.search_locations.side_effect = Exception(
            "Location API Error"
        )

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_extended_forecast("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_hourly_forecast_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location hourly forecast retrieval"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_hourly_forecast(
            "New York", 168, "en-us"
        )

        assert result["success"] is True
        assert "location" in result
        assert "forecasts" in result
        assert result["hours"] == 168

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_hourly_forecast_no_locations(self, mock_weather_client):
        """Test location hourly forecast with no locations found"""
        mock_weather_client.search_locations.return_value = []

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_hourly_forecast("NonexistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_hourly_forecast_error(self, mock_weather_client):
        """Test location hourly forecast error handling"""
        mock_weather_client.search_locations.side_effect = Exception(
            "Location API Error"
        )

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_hourly_forecast("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]
