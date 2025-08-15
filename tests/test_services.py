"""
Unit tests for weather service classes
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from weather_mcp.services import (
    LocationService, WeatherService, ForecastService,
    AlertService, RawWeatherService
)


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
        location_service = LocationService(mock_weather_client)
        result = await location_service.search_locations("Paris")

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

        location_service = LocationService(mock_weather_client)
        result = await location_service.search_locations("New York")

        assert result["success"] is False
        assert "API Error" in result["error"]


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

        # Verify the mock was called correctly
        mock_weather_client.get_current_weather.assert_called_once_with(
            "40.7128,-74.0060", True
        )

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

        # Verify the mock was called correctly with default details=True
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

        weather_service = WeatherService(mock_weather_client)
        result = await weather_service.get_current_weather("40.7128,-74.0060")

        assert result["success"] is False
        assert "Weather API Error" in result["error"]


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
        assert forecast_data["date"] == "2024-01-15"
        assert forecast_data["min_temperature"] == 2.0
        assert forecast_data["max_temperature"] == 8.0
        assert forecast_data["temperature_unit"] == "C"
        assert forecast_data["day_weather_text"] == "Sunny"
        assert forecast_data["day_precipitation_probability"] == 10

        # Verify the mock was called correctly
        mock_weather_client.get_5day_forecast.assert_called_once_with(
            "40.7128,-74.0060", True
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_extended_forecast_success(self, mock_weather_client):
        """Test successful extended forecast retrieval"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_extended_forecast("40.7128,-74.0060", 7, True)

        assert result["success"] is True
        assert result["count"] == 1
        assert result["days"] == 7

        forecast_data = result["forecasts"][0]
        assert forecast_data["date"] == "2024-01-15"
        assert forecast_data["min_temperature"] == 2.0
        assert forecast_data["max_temperature"] == 8.0

        # Verify the mock was called correctly
        mock_weather_client.get_daily_forecast.assert_called_once_with(
            "40.7128,-74.0060", 7, True
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_success(self, mock_weather_client):
        """Test successful hourly forecast retrieval"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_hourly_forecast("40.7128,-74.0060", 24, True)

        assert result["success"] is True
        assert result["count"] == 1
        assert result["hours"] == 24

        forecast_data = result["forecasts"][0]
        assert forecast_data["timestamp"] == "2024-01-15T12:00:00"
        assert forecast_data["temperature"] == 5.0
        assert forecast_data["humidity"] == 65

        # Verify the mock was called correctly
        mock_weather_client.get_hourly_forecast.assert_called_once_with(
            "40.7128,-74.0060", 24, True
        )


class TestAlertService:
    """Test class for AlertService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_alerts_success(self, mock_weather_client):
        """Test successful weather alerts retrieval"""
        alert_service = AlertService(mock_weather_client)
        result = await alert_service.get_weather_alerts("40.7128,-74.0060")

        assert result["success"] is True
        assert result["count"] == 1

        alert = result["alerts"][0]
        assert alert["alert_id"] == "ALERT123"
        assert alert["title"] == "Winter Weather Advisory"
        assert alert["severity"] == "Minor"
        assert alert["category"] == "Weather"

        # Verify the mock was called correctly
        mock_weather_client.get_weather_alerts.assert_called_once_with("40.7128,-74.0060")

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


class TestRawWeatherService:
    """Test class for RawWeatherService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_success(self, mock_weather_client):
        """Test successful detailed raw weather data retrieval"""
        raw_weather_service = RawWeatherService(mock_weather_client)
        result = await raw_weather_service.get_detailed_grid_data("40.7128,-74.0060", True)

        assert result["success"] is True
        assert result["count"] == 1

        grid_data = result["grid_data"][0]
        assert grid_data["timestamp"] == "2024-01-15T12:00:00"
        assert grid_data["temperature"] == 5.0
        assert grid_data["dewpoint"] == -2.0
        assert grid_data["relative_humidity"] == 65.0

        # Verify the mock was called correctly
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
