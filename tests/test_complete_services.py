"""
Comprehensive unit tests for all weather service classes and their methods
"""

from datetime import datetime
from unittest.mock import AsyncMock, patch

import pytest

from weather_mcp.services import (
    LocationService, WeatherService, ForecastService,
    AlertService, RawWeatherService
)


class TestLocationServiceComplete:
    """Complete test coverage for LocationService"""

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
    async def test_get_location_weather_success(self, mock_weather_client, sample_location_search_response):
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
        mock_weather_client.search_locations.side_effect = Exception("Location API Error")

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_weather("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_forecast_success(self, mock_weather_client, sample_location_search_response):
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
        mock_weather_client.search_locations.side_effect = Exception("Location API Error")

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_forecast("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_alerts_success(self, mock_weather_client, sample_location_search_response):
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
        mock_weather_client.search_locations.side_effect = Exception("Location API Error")

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_alerts("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_success(self, mock_weather_client, sample_location_search_response):
        """Test successful location extended forecast retrieval"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_extended_forecast("New York", 7, "en-us")

        assert result["success"] is True
        assert "location" in result
        assert "forecasts" in result
        assert result["days"] == 7

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_no_locations(self, mock_weather_client):
        """Test location extended forecast with no locations found"""
        mock_weather_client.search_locations.return_value = []

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_extended_forecast("NonexistentPlace")

        assert result["success"] is False
        assert "No locations found" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_extended_forecast_error(self, mock_weather_client):
        """Test location extended forecast error handling"""
        mock_weather_client.search_locations.side_effect = Exception("Location API Error")

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_extended_forecast("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_hourly_forecast_success(self, mock_weather_client, sample_location_search_response):
        """Test successful location hourly forecast retrieval"""
        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_hourly_forecast("New York", 168, "en-us")

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
        mock_weather_client.search_locations.side_effect = Exception("Location API Error")

        location_service = LocationService(mock_weather_client)
        result = await location_service.get_location_hourly_forecast("New York")

        assert result["success"] is False
        assert "Location API Error" in result["error"]


class TestWeatherServiceComplete:
    """Complete test coverage for WeatherService"""

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
        mock_weather_client.get_current_weather.side_effect = Exception("Weather API Error")

        weather_service = WeatherService(mock_weather_client)
        result = await weather_service.get_current_weather("40.7128,-74.0060")

        assert result["success"] is False
        assert "Weather API Error" in result["error"]


class TestForecastServiceComplete:
    """Complete test coverage for ForecastService"""

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
        mock_weather_client.get_5day_forecast.side_effect = Exception("Forecast API Error")

        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_5day_forecast("40.7128,-74.0060")

        assert result["success"] is False
        assert "Forecast API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_extended_forecast_success(self, mock_weather_client):
        """Test successful extended forecast retrieval"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_extended_forecast("40.7128,-74.0060", 7, True)

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
        mock_weather_client.get_daily_forecast.side_effect = Exception("Extended Forecast API Error")

        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_extended_forecast("40.7128,-74.0060")

        assert result["success"] is False
        assert "Extended Forecast API Error" in result["error"]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_success(self, mock_weather_client):
        """Test successful hourly forecast retrieval"""
        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_hourly_forecast("40.7128,-74.0060", 24, True)

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
        mock_weather_client.get_hourly_forecast.side_effect = Exception("Hourly Forecast API Error")

        forecast_service = ForecastService(mock_weather_client)
        result = await forecast_service.get_hourly_forecast("40.7128,-74.0060")

        assert result["success"] is False
        assert "Hourly Forecast API Error" in result["error"]


class TestAlertServiceComplete:
    """Complete test coverage for AlertService"""

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
        mock_weather_client.get_weather_alerts.side_effect = Exception("Alerts API Error")

        alert_service = AlertService(mock_weather_client)
        result = await alert_service.get_weather_alerts("40.7128,-74.0060")

        assert result["success"] is False
        assert "Alerts API Error" in result["error"]


class TestRawWeatherServiceComplete:
    """Complete test coverage for RawWeatherService"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_success(self, mock_weather_client):
        """Test successful detailed raw weather data retrieval"""
        raw_weather_service = RawWeatherService(mock_weather_client)
        result = await raw_weather_service.get_detailed_grid_data("40.7128,-74.0060", True)

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
        mock_weather_client.get_detailed_grid_data.assert_called_once_with("40.7128,-74.0060", True)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_detailed_grid_data_error(self, mock_weather_client):
        """Test get_detailed_grid_data error handling"""
        mock_weather_client.get_detailed_grid_data.side_effect = Exception("Raw Weather Data API Error")

        raw_weather_service = RawWeatherService(mock_weather_client)
        result = await raw_weather_service.get_detailed_grid_data("40.7128,-74.0060")

        assert result["success"] is False
        assert "Raw Weather Data API Error" in result["error"]
