"""
Unit tests for FastMCP weather tool functions
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from weather_mcp.services import (
    LocationService, WeatherService, ForecastService,
    AlertService, GridDataService
)
from main import weather_client


class TestWeatherTools:
    """Test class for all weather tool functions"""

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

        # Verify the mock was called correctly
        mock_weather_client.search_locations.assert_called_once_with(
            "New York", "en-us"
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_locations_without_language(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test location search with default language"""
        result = await search_locations_impl(mock_weather_client, "Paris")

        assert result["success"] is True
        assert result["locations"] == sample_location_search_response
        mock_weather_client.search_locations.assert_called_once_with(
                "Paris", "en-us"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_locations_error(self, mock_weather_client):
        """Test search_locations error handling"""
        mock_weather_client.search_locations.side_effect = Exception("API Error")

        result = await search_locations_impl(mock_weather_client, "New York")

        assert result["success"] is False
        assert "API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, mock_weather_client):
        """Test successful current weather retrieval"""

        result = await get_current_weather_impl(mock_weather_client, "40.7128,-74.0060", True)

        assert result["success"] is True

        weather = result["weather"]
        assert weather["temperature"] == 5.0
        assert weather["temperature_unit"] == "C"
        assert weather["humidity"] == 65
        assert weather["wind_speed"] == 15.0
        assert weather["wind_direction"] == "SW"
        assert weather["weather_text"] == "Partly Cloudy"
        assert weather["uv_index"] == 2

        mock_weather_client.get_current_weather.assert_called_once_with(
                "40.7128,-74.0060", True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_default_details(self, mock_weather_client):
        """Test current weather with default details parameter"""

        result = await get_current_weather_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is True
        mock_weather_client.get_current_weather.assert_called_once_with(
                "40.7128,-74.0060", True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_error(self, mock_weather_client):
        """Test get_current_weather error handling"""

        mock_weather_client.get_current_weather.side_effect = Exception(
            "Weather API Error"
        )

        result = await get_current_weather_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is False
        assert "Weather API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_5day_forecast_success(self, mock_weather_client):
        """Test successful weather forecast retrieval"""

        result = await get_5day_forecast_impl(mock_weather_client, "40.7128,-74.0060", True)

        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["forecasts"]) == 1

        forecast_data = result["forecasts"][0]
        assert forecast_data["min_temperature"] == -2.0
        assert forecast_data["max_temperature"] == 5.0
        assert forecast_data["day_weather_text"] == "Partly Cloudy"
        assert forecast_data["night_weather_text"] == "Clear"

        mock_weather_client.get_5day_forecast.assert_called_once_with(
                "40.7128,-74.0060", True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_5day_forecast_default_metric(self, mock_weather_client):
        """Test weather forecast with default metric parameter"""

        result = await get_5day_forecast_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is True
        mock_weather_client.get_5day_forecast.assert_called_once_with(
                "40.7128,-74.0060", True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_5day_forecast_error(self, mock_weather_client):
        """Test get_5day_forecast error handling"""

        mock_weather_client.get_5day_forecast.side_effect = Exception(
                "Forecast API Error"
            )

        result = await get_5day_forecast_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is False
        assert "Forecast API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_alerts_success(self, mock_weather_client):
        """Test successful weather alerts retrieval"""

        result = await get_weather_alerts_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is True
        assert result["count"] == 1
        assert len(result["alerts"]) == 1

        alert = result["alerts"][0]
        assert alert["alert_id"] == "12345"
        assert alert["title"] == "Winter Storm Warning"
        assert alert["severity"] == "Moderate"
        assert alert["category"] == "meteorological"
        assert alert["areas"] == ["New York County"]

        mock_weather_client.get_weather_alerts.assert_called_once_with(
                "40.7128,-74.0060"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_alerts_error(self, mock_weather_client):
        """Test get_weather_alerts error handling"""

        mock_weather_client.get_weather_alerts.side_effect = Exception(
                "Alerts API Error"
            )

        result = await get_weather_alerts_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is False
        assert "Alerts API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_weather_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location weather retrieval"""

            # Mock the search to return our location data
        mock_weather_client.search_locations.return_value = (
                sample_location_search_response
            )

        result = await get_location_weather_impl(mock_weather_client, "New York")

        assert result["success"] is True
        assert result["location"] == sample_location_search_response[0]
        assert result["weather"]["temperature"] == 5.0
        assert result["weather"]["weather_text"] == "Partly Cloudy"

        mock_weather_client.search_locations.assert_called_once_with(
                "New York", "en-us"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_weather_no_locations(self, mock_weather_client):
        """Test location weather when no locations found"""

        mock_weather_client.search_locations.return_value = []

        result = await get_location_weather_impl(mock_weather_client, "NonExistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_weather_error(self, mock_weather_client):
        """Test get_location_weather error handling"""

        mock_weather_client.search_locations.side_effect = Exception(
                "Location API Error"
            )

        result = await get_location_weather_impl(mock_weather_client, "New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_forecast_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location forecast retrieval"""

            # Mock the search to return our location data
        mock_weather_client.search_locations.return_value = (
                sample_location_search_response
            )

        result = await get_location_forecast_impl(mock_weather_client, "New York")

        assert result["success"] is True
        assert result["location"] == sample_location_search_response[0]
        assert result["count"] == 1
        assert len(result["forecasts"]) == 1

        mock_weather_client.search_locations.assert_called_once_with(
                "New York", "en-us"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_forecast_no_locations(self, mock_weather_client):
        """Test location forecast when no locations found"""

        mock_weather_client.search_locations.return_value = []

        result = await get_location_forecast_impl(mock_weather_client, "NonExistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_forecast_error(self, mock_weather_client):
        """Test get_location_forecast error handling"""

        mock_weather_client.search_locations.side_effect = Exception(
                "Location API Error"
            )

        result = await get_location_forecast_impl(mock_weather_client, "New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_alerts_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location alerts retrieval"""

            # Mock the search to return our location data
        mock_weather_client.search_locations.return_value = (
                sample_location_search_response
            )

        result = await get_location_alerts_impl(mock_weather_client, "New York")

        assert result["success"] is True
        assert result["location"] == sample_location_search_response[0]
        assert result["count"] == 1
        assert len(result["alerts"]) == 1

        mock_weather_client.search_locations.assert_called_once_with(
                "New York", "en-us"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_alerts_no_locations(self, mock_weather_client):
        """Test location alerts when no locations found"""

        mock_weather_client.search_locations.return_value = []

        result = await get_location_alerts_impl(mock_weather_client, "NonExistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_alerts_error(self, mock_weather_client):
        """Test get_location_alerts error handling"""

        mock_weather_client.search_locations.side_effect = Exception(
                "Location API Error"
            )

        result = await get_location_alerts_impl(mock_weather_client, "New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_extended_forecast_success(self, mock_weather_client):
        """Test successful extended forecast retrieval"""

        result = await get_extended_forecast_impl(mock_weather_client, "40.7128,-74.0060", days=7, metric=True)

        assert result["success"] is True
        assert result["count"] == 3
        assert len(result["forecasts"]) == 3

        forecast_data = result["forecasts"][0]
        assert forecast_data["min_temperature"] == -2.0
        assert forecast_data["max_temperature"] == 5.0
        assert forecast_data["day_weather_text"] == "Partly Cloudy"
        assert forecast_data["night_weather_text"] == "Clear"

        mock_weather_client.get_daily_forecast.assert_called_once_with(
                "40.7128,-74.0060", 7, True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_extended_forecast_default_params(self, mock_weather_client):
        """Test extended forecast with default parameters"""

        result = await get_extended_forecast_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is True
        mock_weather_client.get_daily_forecast.assert_called_once_with(
                "40.7128,-74.0060", 7, True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_extended_forecast_error(self, mock_weather_client):
        """Test get_extended_forecast error handling"""

        mock_weather_client.get_daily_forecast.side_effect = Exception(
                "Extended Forecast API Error"
            )

        result = await get_extended_forecast_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is False
        assert "Extended Forecast API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_success(self, mock_weather_client):
        """Test successful hourly forecast retrieval"""

        result = await get_hourly_forecast_impl(mock_weather_client, "40.7128,-74.0060", hours=24, metric=True)

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["forecasts"]) == 2

        forecast_data = result["forecasts"][0]
        assert forecast_data["temperature"] == 6.0
        assert forecast_data["temperature_unit"] == "C"
        assert forecast_data["humidity"] == 60
        assert forecast_data["weather_text"] == "Partly Cloudy"
        assert forecast_data["precipitation_probability"] == 10

        mock_weather_client.get_hourly_forecast.assert_called_once_with(
                "40.7128,-74.0060", 24, True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_default_params(self, mock_weather_client):
        """Test hourly forecast with default parameters"""

        result = await get_hourly_forecast_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is True
        mock_weather_client.get_hourly_forecast.assert_called_once_with(
                "40.7128,-74.0060", 168, True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_error(self, mock_weather_client):
        """Test get_hourly_forecast error handling"""

        mock_weather_client.get_hourly_forecast.side_effect = Exception(
                "Hourly Forecast API Error"
            )

        result = await get_hourly_forecast_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is False
        assert "Hourly Forecast API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_success(self, mock_weather_client):
        """Test successful detailed grid data retrieval"""

        result = await get_detailed_grid_data_impl(mock_weather_client, "40.7128,-74.0060", metric=True)

        assert result["success"] is True
        assert result["count"] == 2
        assert len(result["grid_data"]) == 2

        grid_data = result["grid_data"][0]
        assert grid_data["temperature"] == 6.0
        assert grid_data["temperature_unit"] == "C"
        assert grid_data["dewpoint"] == 2.0
        assert grid_data["relative_humidity"] == 60
        assert grid_data["wind_speed"] == 15.0
        assert grid_data["pressure"] == 1015.0
        assert grid_data["apparent_temperature"] == 5.5
        assert grid_data["heat_index"] == 6.0

        mock_weather_client.get_detailed_grid_data.assert_called_once_with(
                "40.7128,-74.0060", True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_default_params(self, mock_weather_client):
        """Test detailed grid data with default parameters"""

        result = await get_detailed_grid_data_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is True
        mock_weather_client.get_detailed_grid_data.assert_called_once_with(
                "40.7128,-74.0060", True
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_error(self, mock_weather_client):
        """Test get_detailed_grid_data error handling"""

        mock_weather_client.get_detailed_grid_data.side_effect = Exception(
                "Grid Data API Error"
            )

        result = await get_detailed_grid_data_impl(mock_weather_client, "40.7128,-74.0060")

        assert result["success"] is False
        assert "Grid Data API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location extended forecast retrieval"""

            # Mock the search to return our location data
        mock_weather_client.search_locations.return_value = (
                sample_location_search_response
            )

        result = await get_location_extended_forecast_impl(mock_weather_client, "New York", days=7)

        assert result["success"] is True
        assert result["location"] == sample_location_search_response[0]
        assert result["count"] == 3
        assert len(result["forecasts"]) == 3

        mock_weather_client.search_locations.assert_called_once_with(
                "New York", "en-us"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_no_locations(self, mock_weather_client):
        """Test location extended forecast when no locations found"""

        mock_weather_client.search_locations.return_value = []

        result = await get_location_extended_forecast_impl(mock_weather_client, "NonExistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_error(self, mock_weather_client):
        """Test get_location_extended_forecast error handling"""

        mock_weather_client.search_locations.side_effect = Exception(
                "Location API Error"
            )

        result = await get_location_extended_forecast_impl(mock_weather_client, "New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_hourly_forecast_success(
        self, mock_weather_client, sample_location_search_response
    ):
        """Test successful location hourly forecast retrieval"""

            # Mock the search to return our location data
        mock_weather_client.search_locations.return_value = (
                sample_location_search_response
            )

        result = await get_location_hourly_forecast_impl(mock_weather_client, "New York", hours=24)

        assert result["success"] is True
        assert result["location"] == sample_location_search_response[0]
        assert result["count"] == 2
        assert len(result["forecasts"]) == 2

        mock_weather_client.search_locations.assert_called_once_with(
                "New York", "en-us"
            )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_hourly_forecast_no_locations(self, mock_weather_client):
        """Test location hourly forecast when no locations found"""

        mock_weather_client.search_locations.return_value = []

        result = await get_location_hourly_forecast_impl(mock_weather_client, "NonExistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_hourly_forecast_error(self, mock_weather_client):
        """Test get_location_hourly_forecast error handling"""

        mock_weather_client.search_locations.side_effect = Exception(
                "Location API Error"
            )

        result = await get_location_hourly_forecast_impl(mock_weather_client, "New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]
