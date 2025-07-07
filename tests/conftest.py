"""
Shared pytest fixtures and mocks for weather MCP server tests
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from typing import Dict, Any, List

from weather_mcp.config import Config
from weather_mcp.accuweather import (
    AccuWeatherClient, 
    CurrentWeather, 
    WeatherForecast, 
    WeatherAlert
)


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing"""
    # Create config with all values explicitly set to avoid .env file interference
    return Config(
        accuweather_api_key="test_api_key_12345",
        accuweather_base_url="https://dataservice.accuweather.com",
        host="localhost",
        port=8000,
        log_level="INFO",
        debug=False,
        log_file=None,
        sse_heartbeat_interval=30,
        sse_max_connections=100,
        cache_ttl_seconds=300,
        cache_max_size=100
    )


@pytest.fixture
def sample_location_search_response():
    """Sample location search response from AccuWeather API"""
    return [
        {
            "Version": 1,
            "Key": "349727",
            "Type": "City",
            "Rank": 10,
            "LocalizedName": "New York",
            "EnglishName": "New York",
            "PrimaryPostalCode": "10001",
            "Region": {
                "ID": "NAM",
                "LocalizedName": "North America",
                "EnglishName": "North America"
            },
            "Country": {
                "ID": "US",
                "LocalizedName": "United States",
                "EnglishName": "United States"
            },
            "AdministrativeArea": {
                "ID": "NY",
                "LocalizedName": "New York",
                "EnglishName": "New York",
                "Level": 1,
                "LocalizedType": "State",
                "EnglishType": "State",
                "CountryID": "US"
            },
            "TimeZone": {
                "Code": "EST",
                "Name": "America/New_York",
                "GmtOffset": -5.0,
                "IsDaylightSaving": False,
                "NextOffsetChange": "2024-03-10T07:00:00Z"
            },
            "GeoPosition": {
                "Latitude": 40.759,
                "Longitude": -73.984,
                "Elevation": {
                    "Metric": {"Value": 57, "Unit": "m"},
                    "Imperial": {"Value": 187, "Unit": "ft"}
                }
            },
            "IsAlias": False,
            "SupplementalAdminAreas": [
                {
                    "Level": 2,
                    "LocalizedName": "New York",
                    "EnglishName": "New York"
                }
            ],
            "DataSets": ["AirQualityCurrentConditions", "AirQualityForecasts"]
        }
    ]


@pytest.fixture
def sample_current_weather_response():
    """Sample current weather response from AccuWeather API"""
    return [
        {
            "LocalObservationDateTime": "2024-01-15T12:00:00-05:00",
            "EpochTime": 1705339200,
            "WeatherText": "Partly sunny",
            "WeatherIcon": 3,
            "HasPrecipitation": False,
            "PrecipitationType": None,
            "IsDayTime": True,
            "Temperature": {
                "Metric": {"Value": 5.0, "Unit": "C", "UnitType": 17},
                "Imperial": {"Value": 41.0, "Unit": "F", "UnitType": 18}
            },
            "MobileLink": "http://www.accuweather.com/en/us/new-york-ny/10001/current-weather/349727",
            "Link": "http://www.accuweather.com/en/us/new-york-ny/10001/current-weather/349727",
            "RelativeHumidity": 65,
            "Wind": {
                "Direction": {"Degrees": 225, "Localized": "SW", "English": "SW"},
                "Speed": {"Metric": {"Value": 15.0, "Unit": "km/h"}, "Imperial": {"Value": 9.3, "Unit": "mi/h"}}
            },
            "Pressure": {
                "Metric": {"Value": 1015.0, "Unit": "mb"}, 
                "Imperial": {"Value": 29.97, "Unit": "inHg"}
            },
            "Visibility": {
                "Metric": {"Value": 16.0, "Unit": "km"}, 
                "Imperial": {"Value": 10.0, "Unit": "mi"}
            },
            "UVIndex": 2,
            "PrecipitationSummary": {
                "Precipitation": {"Metric": {"Value": 0.0, "Unit": "mm"}}
            }
        }
    ]


@pytest.fixture
def sample_forecast_response():
    """Sample 5-day forecast response from AccuWeather API"""
    return {
        "Headline": {
            "EffectiveDate": "2024-01-16T07:00:00-05:00",
            "EffectiveEpochDate": 1705406400,
            "Severity": 4,
            "Text": "Expect cold conditions Tuesday",
            "Category": "cold",
            "EndDate": "2024-01-16T19:00:00-05:00",
            "EndEpochDate": 1705449600,
            "MobileLink": "http://www.accuweather.com/en/us/new-york-ny/10001/daily-weather-forecast/349727",
            "Link": "http://www.accuweather.com/en/us/new-york-ny/10001/daily-weather-forecast/349727"
        },
        "DailyForecasts": [
            {
                "Date": "2024-01-15T07:00:00-05:00",
                "EpochDate": 1705320000,
                "Temperature": {
                    "Minimum": {"Value": -2.0, "Unit": "C", "UnitType": 17},
                    "Maximum": {"Value": 5.0, "Unit": "C", "UnitType": 17}
                },
                "Day": {
                    "Icon": 3,
                    "IconPhrase": "Partly sunny",
                    "HasPrecipitation": False
                },
                "Night": {
                    "Icon": 33,
                    "IconPhrase": "Clear",
                    "HasPrecipitation": False
                },
                "Sources": ["AccuWeather"],
                "MobileLink": "http://www.accuweather.com/en/us/new-york-ny/10001/daily-weather-forecast/349727",
                "Link": "http://www.accuweather.com/en/us/new-york-ny/10001/daily-weather-forecast/349727"
            }
        ]
    }


@pytest.fixture
def sample_weather_alerts_response():
    """Sample weather alerts response from AccuWeather API"""
    return [
        {
            "AlertID": "12345",
            "Title": "Winter Storm Warning",
            "Description": "Heavy snow expected. Total snow accumulations of 6 to 10 inches possible.",
            "Priority": 2,
            "Class": "meteorological",
            "Classification": "Moderate",
            "StartTime": "2024-01-16T00:00:00-05:00",
            "EndTime": "2024-01-17T12:00:00-05:00",
            "Source": "NWS",
            "SourceId": "2.49.0.1.840.0.1b9fcec98e2e00423e7b6e37ad2b55b7a9bb69e0",
            "Areas": [
                {
                    "Text": "New York County",
                    "StartTime": "2024-01-16T00:00:00-05:00",
                    "EndTime": "2024-01-17T12:00:00-05:00"
                }
            ]
        }
    ]


@pytest.fixture
def sample_hourly_forecast_response():
    """Sample hourly forecast response from AccuWeather API"""
    return [
        {
            "DateTime": "2024-01-15T13:00:00-05:00",
            "EpochDateTime": 1705342800,
            "WeatherIcon": 3,
            "IconPhrase": "Partly sunny",
            "HasPrecipitation": False,
            "Temperature": {"Value": 6.0, "Unit": "C", "UnitType": 17},
            "RealFeelTemperature": {"Value": 2.0, "Unit": "C", "UnitType": 17},
            "Wind": {
                "Speed": {"Value": 15.0, "Unit": "km/h", "UnitType": 7},
                "Direction": {"Degrees": 225, "Localized": "SW", "English": "SW"}
            },
            "RelativeHumidity": 60,
            "Visibility": {"Value": 16.0, "Unit": "km", "UnitType": 6},
            "UVIndex": 2,
            "PrecipitationProbability": 10
        }
    ]


@pytest.fixture
def mock_weather_client(mock_config, sample_location_search_response, 
                       sample_current_weather_response, sample_forecast_response,
                       sample_weather_alerts_response, sample_hourly_forecast_response):
    """Create a mock AccuWeatherClient with predefined responses"""
    client = AsyncMock(spec=AccuWeatherClient)
    
    # Mock configuration
    client.config = mock_config
    
    # Mock context manager methods
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)
    
    # Mock API methods
    client.search_locations = AsyncMock(return_value=sample_location_search_response)
    client.get_location_key = AsyncMock(return_value="349727")
    
    # Mock current weather with proper CurrentWeather object
    mock_current_weather = CurrentWeather(
        location_key="349727",
        location_name="New York",
        temperature=5.0,
        temperature_unit="C",
        humidity=65,
        wind_speed=15.0,
        wind_direction="SW",
        pressure=1015.0,
        visibility=16.0,
        uv_index=2,
        weather_text="Partly sunny",
        weather_icon=3,
        precipitation=0.0,
        local_time=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    )
    client.get_current_weather = AsyncMock(return_value=mock_current_weather)
    
    # Mock forecast with proper WeatherForecast objects
    mock_forecast = [
        WeatherForecast(
            date=datetime(2024, 1, 15, 7, 0, 0, tzinfo=timezone.utc),
            day_temperature=5.0,
            night_temperature=-2.0,
            day_weather_text="Partly sunny",
            night_weather_text="Clear",
            day_icon=3,
            night_icon=33,
            precipitation_probability=0,
            precipitation_amount=0.0,
            wind_speed=15.0,
            wind_direction="SW"
        )
    ]
    client.get_5day_forecast = AsyncMock(return_value=mock_forecast)
    
    # Mock alerts with proper WeatherAlert objects
    mock_alerts = [
        WeatherAlert(
            alert_id="12345",
            title="Winter Storm Warning",
            description="Heavy snow expected. Total snow accumulations of 6 to 10 inches possible.",
            severity="Moderate",
            category="meteorological",
            start_time=datetime(2024, 1, 16, 0, 0, 0, tzinfo=timezone.utc),
            end_time=datetime(2024, 1, 17, 12, 0, 0, tzinfo=timezone.utc),
            areas=["New York County"]
        )
    ]
    client.get_weather_alerts = AsyncMock(return_value=mock_alerts)
    
    # Mock other methods
    client.get_hourly_forecast = AsyncMock(return_value=sample_hourly_forecast_response)
    client.get_indices = AsyncMock(return_value={"airquality": {"value": 45, "category": "good"}})
    client.get_historical_weather = AsyncMock(return_value=[{"date": "2024-01-10", "temperature": 3.0}])
    
    return client


@pytest.fixture
def mock_fastmcp_server():
    """Create a mock FastMCP server for testing"""
    from fastmcp import FastMCP
    
    server = MagicMock(spec=FastMCP)
    server.run = AsyncMock()
    return server


@pytest.fixture
async def mock_server_environment(mock_config, mock_weather_client):
    """Set up a complete mock environment for server testing"""
    with patch('weather_mcp.server.weather_client', mock_weather_client):
        with patch('weather_mcp.server.get_config', return_value=mock_config):
            with patch('weather_mcp.server.setup_logging'):
                yield {
                    'config': mock_config,
                    'weather_client': mock_weather_client
                } 