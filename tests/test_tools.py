"""
Unit tests for FastMCP weather tool functions
"""

import pytest
from unittest.mock import patch, AsyncMock
from datetime import datetime

from weather_mcp.server import (
    _search_locations_impl,
    _get_location_key_impl,
    _get_current_weather_impl,
    _get_weather_forecast_impl,
    _get_hourly_forecast_impl,
    _get_weather_alerts_impl,
    _get_weather_indices_impl,
    _get_historical_weather_impl,
    weather_client
)


class TestWeatherTools:
    """Test class for all weather tool functions"""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_locations_success(self, mock_weather_client, sample_location_search_response):
        """Test successful location search"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _search_locations_impl("New York", "en-us")
            
            assert result["tool"] == "search_locations"
            assert result["query"] == "New York"
            assert result["results"] == sample_location_search_response
            assert len(result["results"]) == 1
            assert result["results"][0]["Key"] == "349727"
            assert result["results"][0]["LocalizedName"] == "New York"
            
            # Verify the mock was called correctly
            mock_weather_client.search_locations.assert_called_once_with("New York", "en-us")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_locations_without_language(self, mock_weather_client, sample_location_search_response):
        """Test location search with default language"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _search_locations_impl("Paris")
            
            assert result["tool"] == "search_locations"
            assert result["query"] == "Paris"
            mock_weather_client.search_locations.assert_called_once_with("Paris", "en-us")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_search_locations_no_client(self):
        """Test search_locations when weather client is not initialized"""
        with patch('weather_mcp.server.weather_client', None):
            with pytest.raises(ValueError, match="Weather client not initialized"):
                await _search_locations_impl("New York")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_key_success(self, mock_weather_client):
        """Test successful location key retrieval from coordinates"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_location_key_impl(40.759, -73.984)
            
            assert result["tool"] == "get_location_key"
            assert result["coordinates"]["latitude"] == 40.759
            assert result["coordinates"]["longitude"] == -73.984
            assert result["location_key"] == "349727"
            
            mock_weather_client.get_location_key.assert_called_once_with(40.759, -73.984)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_location_key_no_client(self):
        """Test get_location_key when weather client is not initialized"""
        with patch('weather_mcp.server.weather_client', None):
            with pytest.raises(ValueError, match="Weather client not initialized"):
                await _get_location_key_impl(40.759, -73.984)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, mock_weather_client):
        """Test successful current weather retrieval"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_current_weather_impl("349727", True)
            
            assert result["tool"] == "get_current_weather"
            assert result["location_key"] == "349727"
            
            weather = result["weather"]
            assert weather["temperature"] == 5.0
            assert weather["temperature_unit"] == "C"
            assert weather["humidity"] == 65
            assert weather["wind_speed"] == 15.0
            assert weather["wind_direction"] == "SW"
            assert weather["weather_text"] == "Partly sunny"
            assert weather["uv_index"] == 2
            
            mock_weather_client.get_current_weather.assert_called_once_with("349727", True)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_default_details(self, mock_weather_client):
        """Test current weather with default details parameter"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_current_weather_impl("349727")
            
            assert result["tool"] == "get_current_weather"
            mock_weather_client.get_current_weather.assert_called_once_with("349727", True)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_current_weather_no_client(self):
        """Test get_current_weather when weather client is not initialized"""
        with patch('weather_mcp.server.weather_client', None):
            with pytest.raises(ValueError, match="Weather client not initialized"):
                await _get_current_weather_impl("349727")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_forecast_success(self, mock_weather_client):
        """Test successful weather forecast retrieval"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_weather_forecast_impl("349727", True)
            
            assert result["tool"] == "get_weather_forecast"
            assert result["location_key"] == "349727"
            assert len(result["forecast"]) == 1
            
            forecast = result["forecast"][0]
            assert forecast["day_temperature"] == 5.0
            assert forecast["night_temperature"] == -2.0
            assert forecast["day_weather_text"] == "Partly sunny"
            assert forecast["night_weather_text"] == "Clear"
            assert forecast["wind_speed"] == 15.0
            assert forecast["wind_direction"] == "SW"
            
            mock_weather_client.get_5day_forecast.assert_called_once_with("349727", True)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_forecast_default_metric(self, mock_weather_client):
        """Test weather forecast with default metric parameter"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_weather_forecast_impl("349727")
            
            assert result["tool"] == "get_weather_forecast"
            mock_weather_client.get_5day_forecast.assert_called_once_with("349727", True)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_forecast_no_client(self):
        """Test get_weather_forecast when weather client is not initialized"""
        with patch('weather_mcp.server.weather_client', None):
            with pytest.raises(ValueError, match="Weather client not initialized"):
                await _get_weather_forecast_impl("349727")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_success(self, mock_weather_client, sample_hourly_forecast_response):
        """Test successful hourly forecast retrieval"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_hourly_forecast_impl("349727", 12)
            
            assert result["tool"] == "get_hourly_forecast"
            assert result["location_key"] == "349727"
            assert result["hours"] == 12
            assert result["forecast"] == sample_hourly_forecast_response
            
            mock_weather_client.get_hourly_forecast.assert_called_once_with("349727", 12)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_default_hours(self, mock_weather_client):
        """Test hourly forecast with default hours parameter"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_hourly_forecast_impl("349727")
            
            assert result["hours"] == 12
            mock_weather_client.get_hourly_forecast.assert_called_once_with("349727", 12)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_hourly_forecast_no_client(self):
        """Test get_hourly_forecast when weather client is not initialized"""
        with patch('weather_mcp.server.weather_client', None):
            with pytest.raises(ValueError, match="Weather client not initialized"):
                await _get_hourly_forecast_impl("349727")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_alerts_success(self, mock_weather_client):
        """Test successful weather alerts retrieval"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_weather_alerts_impl("349727")
            
            assert result["tool"] == "get_weather_alerts"
            assert result["location_key"] == "349727"
            assert len(result["alerts"]) == 1
            
            alert = result["alerts"][0]
            assert alert["alert_id"] == "12345"
            assert alert["title"] == "Winter Storm Warning"
            assert alert["severity"] == "Moderate"
            assert alert["category"] == "meteorological"
            assert "New York County" in alert["areas"]
            
            mock_weather_client.get_weather_alerts.assert_called_once_with("349727")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_alerts_no_client(self):
        """Test get_weather_alerts when weather client is not initialized"""
        with patch('weather_mcp.server.weather_client', None):
            with pytest.raises(ValueError, match="Weather client not initialized"):
                await _get_weather_alerts_impl("349727")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_indices_success(self, mock_weather_client):
        """Test successful weather indices retrieval"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_weather_indices_impl("349727", 1)
            
            assert result["tool"] == "get_weather_indices"
            assert result["location_key"] == "349727"
            assert result["index_id"] == 1
            assert result["indices"]["airquality"]["value"] == 45
            assert result["indices"]["airquality"]["category"] == "good"
            
            mock_weather_client.get_indices.assert_called_once_with("349727", 1)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_indices_default_index(self, mock_weather_client):
        """Test weather indices with default index_id parameter"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            result = await _get_weather_indices_impl("349727")
            
            assert result["index_id"] == 1
            mock_weather_client.get_indices.assert_called_once_with("349727", 1)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_weather_indices_no_client(self):
        """Test get_weather_indices when weather client is not initialized"""
        with patch('weather_mcp.server.weather_client', None):
            with pytest.raises(ValueError, match="Weather client not initialized"):
                await _get_weather_indices_impl("349727")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_historical_weather_success(self, mock_weather_client):
        """Test successful historical weather retrieval"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            start_date = "2024-01-10T00:00:00"
            end_date = "2024-01-15T00:00:00"
            
            result = await _get_historical_weather_impl("349727", start_date, end_date)
            
            assert result["tool"] == "get_historical_weather"
            assert result["location_key"] == "349727"
            assert result["start_date"] == start_date
            assert result["end_date"] == end_date
            assert len(result["historical_data"]) == 1
            assert result["historical_data"][0]["date"] == "2024-01-10"
            assert result["historical_data"][0]["temperature"] == 3.0
            
            # Verify the mock was called with datetime objects
            mock_weather_client.get_historical_weather.assert_called_once()
            call_args = mock_weather_client.get_historical_weather.call_args[0]
            assert call_args[0] == "349727"
            assert isinstance(call_args[1], datetime)
            assert isinstance(call_args[2], datetime)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_historical_weather_no_client(self):
        """Test get_historical_weather when weather client is not initialized"""
        with patch('weather_mcp.server.weather_client', None):
            with pytest.raises(ValueError, match="Weather client not initialized"):
                await _get_historical_weather_impl("349727", "2024-01-10T00:00:00", "2024-01-15T00:00:00")

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_historical_weather_invalid_date_format(self, mock_weather_client):
        """Test historical weather with invalid date format"""
        with patch('weather_mcp.server.weather_client', mock_weather_client):
            with pytest.raises(ValueError):
                await _get_historical_weather_impl("349727", "invalid-date", "2024-01-15T00:00:00") 