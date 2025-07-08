"""
Shared pytest fixtures and mocks for weather MCP server tests
"""

from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from weather_mcp.config import Config
from weather_mcp.nws import (
    CurrentWeather,
    NationalWeatherServiceClient,
    WeatherAlert,
    WeatherForecast,
    HourlyForecast,
    DetailedGridData,
)


@pytest.fixture
def mock_config():
    """Create a mock configuration for testing NWS"""
    # Create config with all values explicitly set to avoid .env file interference
    return Config(
        host="0.0.0.0",  # Use the actual default value
        port=8000,
        log_level="INFO",
        debug=False,
        sse_heartbeat_interval=30,
        sse_max_connections=100,
        cache_ttl_seconds=300,
        cache_max_size=100,
    )


@pytest.fixture
def sample_location_search_response():
    """Sample location search response from NWS geocoding API"""
    return [
        {
            "Key": "40.7127753,-74.0059728",
            "LocalizedName": "New York",
            "AdministrativeArea": {"LocalizedName": "New York"},
            "Country": {"LocalizedName": "United States"},
            "GeoPosition": {"Latitude": 40.7127753, "Longitude": -74.0059728},
            "place_id": 123456,
            "licence": "Data OpenStreetMap",
            "osm_type": "relation",
            "osm_id": 175905,
            "lat": "40.7127753",
            "lon": "-74.0059728",
            "display_name": "New York, New York County, New York, United States",
            "address": {
                "city": "New York",
                "county": "New York County",
                "state": "New York",
                "country": "United States",
                "postcode": "10001",
            },
            "boundingbox": ["40.4773991", "40.9175771", "-74.2590879", "-73.7004845"],
        }
    ]


@pytest.fixture
def sample_current_weather_response():
    """Sample current weather response from NWS observations API"""
    return {
        "properties": {
            "timestamp": "2024-01-15T17:00:00+00:00",
            "textDescription": "Partly Cloudy",
            "temperature": {
                "value": 5.0,
                "unitCode": "wmoUnit:degC",
                "qualityControl": "V",
            },
            "dewpoint": {
                "value": -2.0,
                "unitCode": "wmoUnit:degC",
                "qualityControl": "V",
            },
            "windDirection": {
                "value": 225,
                "unitCode": "wmoUnit:degree_(angle)",
                "qualityControl": "V",
            },
            "windSpeed": {
                "value": 15.0,
                "unitCode": "wmoUnit:km_h-1",
                "qualityControl": "V",
            },
            "windGust": {
                "value": None,
                "unitCode": "wmoUnit:km_h-1",
                "qualityControl": "Z",
            },
            "barometricPressure": {
                "value": 101500,
                "unitCode": "wmoUnit:Pa",
                "qualityControl": "V",
            },
            "seaLevelPressure": {
                "value": 101500,
                "unitCode": "wmoUnit:Pa",
                "qualityControl": "V",
            },
            "visibility": {
                "value": 16000,
                "unitCode": "wmoUnit:m",
                "qualityControl": "V",
            },
            "relativeHumidity": {
                "value": 65,
                "unitCode": "wmoUnit:percent",
                "qualityControl": "V",
            },
            "windChill": {
                "value": None,
                "unitCode": "wmoUnit:degC",
                "qualityControl": "Z",
            },
            "heatIndex": {
                "value": None,
                "unitCode": "wmoUnit:degC",
                "qualityControl": "Z",
            },
            "precipitationLastHour": {
                "value": 0,
                "unitCode": "wmoUnit:mm",
                "qualityControl": "V",
            },
        }
    }


@pytest.fixture
def sample_forecast_response():
    """Sample 5-day forecast response from NWS forecast API"""
    return {
        "properties": {
            "periods": [
                {
                    "number": 1,
                    "name": "Today",
                    "startTime": "2024-01-15T06:00:00-05:00",
                    "endTime": "2024-01-15T18:00:00-05:00",
                    "isDaytime": True,
                    "temperature": 41,
                    "temperatureUnit": "F",
                    "temperatureTrend": None,
                    "windSpeed": "5 to 10 mph",
                    "windDirection": "SW",
                    "icon": "https://api.weather.gov/icons/land/day/sct?size=medium",
                    "shortForecast": "Partly Cloudy",
                    "detailedForecast": "Partly cloudy, with a high near 41. Southwest wind 5 to 10 mph.",
                },
                {
                    "number": 2,
                    "name": "Tonight",
                    "startTime": "2024-01-15T18:00:00-05:00",
                    "endTime": "2024-01-16T06:00:00-05:00",
                    "isDaytime": False,
                    "temperature": 28,
                    "temperatureUnit": "F",
                    "temperatureTrend": None,
                    "windSpeed": "5 mph",
                    "windDirection": "SW",
                    "icon": "https://api.weather.gov/icons/land/night/clear?size=medium",
                    "shortForecast": "Clear",
                    "detailedForecast": "Clear, with a low around 28. Southwest wind around 5 mph.",
                },
                {
                    "number": 3,
                    "name": "Tuesday",
                    "startTime": "2024-01-16T06:00:00-05:00",
                    "endTime": "2024-01-16T18:00:00-05:00",
                    "isDaytime": True,
                    "temperature": 38,
                    "temperatureUnit": "F",
                    "temperatureTrend": None,
                    "windSpeed": "5 to 10 mph",
                    "windDirection": "W",
                    "icon": "https://api.weather.gov/icons/land/day/few?size=medium",
                    "shortForecast": "Sunny",
                    "detailedForecast": "Sunny, with a high near 38. West wind 5 to 10 mph.",
                },
                {
                    "number": 4,
                    "name": "Tuesday Night",
                    "startTime": "2024-01-16T18:00:00-05:00",
                    "endTime": "2024-01-17T06:00:00-05:00",
                    "isDaytime": False,
                    "temperature": 25,
                    "temperatureUnit": "F",
                    "temperatureTrend": None,
                    "windSpeed": "5 mph",
                    "windDirection": "W",
                    "icon": "https://api.weather.gov/icons/land/night/clear?size=medium",
                    "shortForecast": "Clear",
                    "detailedForecast": "Clear, with a low around 25. West wind around 5 mph.",
                },
                {
                    "number": 5,
                    "name": "Wednesday",
                    "startTime": "2024-01-17T06:00:00-05:00",
                    "endTime": "2024-01-17T18:00:00-05:00",
                    "isDaytime": True,
                    "temperature": 42,
                    "temperatureUnit": "F",
                    "temperatureTrend": None,
                    "windSpeed": "5 to 10 mph",
                    "windDirection": "SW",
                    "icon": "https://api.weather.gov/icons/land/day/sct?size=medium",
                    "shortForecast": "Partly Cloudy",
                    "detailedForecast": "Partly cloudy, with a high near 42. Southwest wind 5 to 10 mph.",
                },
            ]
        }
    }


@pytest.fixture
def sample_weather_alerts_response():
    """Sample weather alerts response from NWS alerts API"""
    return {
        "features": [
            {
                "id": "https://api.weather.gov/alerts/urn:oid:2.49.0.1.840.0.12345",
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [-74.0059, 40.7128],
                            [-74.0059, 40.8000],
                            [-73.9000, 40.8000],
                            [-73.9000, 40.7128],
                            [-74.0059, 40.7128],
                        ]
                    ],
                },
                "properties": {
                    "id": "urn:oid:2.49.0.1.840.0.12345",
                    "areaDesc": "New York County",
                    "geocode": {"FIPS6": ["036061"], "UGC": ["NYZ072"]},
                    "affectedZones": ["https://api.weather.gov/zones/forecast/NYZ072"],
                    "references": [],
                    "sent": "2024-01-16T00:00:00-05:00",
                    "effective": "2024-01-16T00:00:00-05:00",
                    "onset": "2024-01-16T00:00:00-05:00",
                    "expires": "2024-01-17T12:00:00-05:00",
                    "ends": "2024-01-17T12:00:00-05:00",
                    "status": "Actual",
                    "messageType": "Alert",
                    "category": "Met",
                    "severity": "Moderate",
                    "certainty": "Likely",
                    "urgency": "Expected",
                    "event": "Winter Storm Warning",
                    "sender": "w-nws.webmaster@noaa.gov",
                    "senderName": "NWS New York NY",
                    "headline": "Winter Storm Warning issued January 16 at 12:00AM EST until January 17 at 12:00PM EST by NWS New York NY",
                    "description": "Heavy snow expected. Total snow accumulations of 6 to 10 inches possible.",
                    "instruction": "Travel could be very difficult. The hazardous conditions could impact the evening commute.",
                },
            }
        ]
    }


@pytest.fixture
def sample_hourly_forecast_response():
    """Sample hourly forecast response from NWS gridpoints API"""
    return {
        "properties": {
            "temperature": {
                "values": [
                    {"validTime": "2024-01-15T13:00:00+00:00", "value": 6.0},
                    {"validTime": "2024-01-15T14:00:00+00:00", "value": 5.5},
                    {"validTime": "2024-01-15T15:00:00+00:00", "value": 5.0},
                ]
            },
            "relativeHumidity": {
                "values": [
                    {"validTime": "2024-01-15T13:00:00+00:00", "value": 60},
                    {"validTime": "2024-01-15T14:00:00+00:00", "value": 62},
                    {"validTime": "2024-01-15T15:00:00+00:00", "value": 65},
                ]
            },
            "windSpeed": {
                "values": [
                    {"validTime": "2024-01-15T13:00:00+00:00", "value": 15.0},
                    {"validTime": "2024-01-15T14:00:00+00:00", "value": 14.0},
                    {"validTime": "2024-01-15T15:00:00+00:00", "value": 13.0},
                ]
            },
            "windDirection": {
                "values": [
                    {"validTime": "2024-01-15T13:00:00+00:00", "value": 225},
                    {"validTime": "2024-01-15T14:00:00+00:00", "value": 220},
                    {"validTime": "2024-01-15T15:00:00+00:00", "value": 215},
                ]
            },
            "probabilityOfPrecipitation": {
                "values": [
                    {"validTime": "2024-01-15T13:00:00+00:00", "value": 10},
                    {"validTime": "2024-01-15T14:00:00+00:00", "value": 5},
                    {"validTime": "2024-01-15T15:00:00+00:00", "value": 0},
                ]
            },
        }
    }


@pytest.fixture
def sample_7day_forecast():
    """Sample 7-day forecast with WeatherForecast objects"""
    return [
        WeatherForecast(
            date=datetime(2024, 1, 15, 7, 0, 0, tzinfo=timezone.utc),
            min_temperature=-2.0,
            max_temperature=5.0,
            temperature_unit="C",
            day_weather_text="Partly Cloudy",
            day_weather_icon=3,
            day_precipitation_probability=0,
            night_weather_text="Clear",
            night_weather_icon=33,
            night_precipitation_probability=0,
        ),
        WeatherForecast(
            date=datetime(2024, 1, 16, 7, 0, 0, tzinfo=timezone.utc),
            min_temperature=-3.0,
            max_temperature=4.0,
            temperature_unit="C",
            day_weather_text="Sunny",
            day_weather_icon=1,
            day_precipitation_probability=0,
            night_weather_text="Clear",
            night_weather_icon=33,
            night_precipitation_probability=0,
        ),
        WeatherForecast(
            date=datetime(2024, 1, 17, 7, 0, 0, tzinfo=timezone.utc),
            min_temperature=-1.0,
            max_temperature=6.0,
            temperature_unit="C",
            day_weather_text="Partly Cloudy",
            day_weather_icon=3,
            day_precipitation_probability=10,
            night_weather_text="Cloudy",
            night_weather_icon=26,
            night_precipitation_probability=20,
        ),
    ]


@pytest.fixture
def sample_hourly_forecast_objects():
    """Sample hourly forecast with HourlyForecast objects"""
    return [
        HourlyForecast(
            timestamp=datetime(2024, 1, 15, 13, 0, 0, tzinfo=timezone.utc),
            temperature=6.0,
            temperature_unit="C",
            humidity=60,
            wind_speed=15.0,
            wind_direction="SW",
            wind_gust=20.0,
            pressure=1015.0,
            visibility=16.0,
            precipitation_probability=10,
            precipitation_amount=0.0,
            weather_text="Partly Cloudy",
            weather_icon=3,
            sky_cover=25,
            dewpoint=2.0,
            apparent_temperature=5.5,
            uv_index=2,
            is_daytime=True,
        ),
        HourlyForecast(
            timestamp=datetime(2024, 1, 15, 14, 0, 0, tzinfo=timezone.utc),
            temperature=5.5,
            temperature_unit="C",
            humidity=62,
            wind_speed=14.0,
            wind_direction="SW",
            wind_gust=18.0,
            pressure=1016.0,
            visibility=15.0,
            precipitation_probability=5,
            precipitation_amount=0.0,
            weather_text="Partly Cloudy",
            weather_icon=3,
            sky_cover=30,
            dewpoint=1.5,
            apparent_temperature=5.0,
            uv_index=2,
            is_daytime=True,
        ),
    ]


@pytest.fixture
def sample_detailed_grid_data():
    """Sample detailed grid data with DetailedGridData objects"""
    return [
        DetailedGridData(
            timestamp=datetime(2024, 1, 15, 13, 0, 0, tzinfo=timezone.utc),
            temperature=6.0,
            dewpoint=2.0,
            max_temperature=7.0,
            min_temperature=5.0,
            relative_humidity=60,
            apparent_temperature=5.5,
            heat_index=6.0,
            wind_chill=4.5,
            sky_cover=25,
            wind_direction=225.0,
            wind_speed=15.0,
            wind_gust=20.0,
            weather_conditions=["Partly Cloudy"],
            probability_of_precipitation=10,
            quantitative_precipitation=0.0,
            ice_accumulation=0.0,
            snowfall_amount=0.0,
            snow_level=0.0,
            ceiling_height=3000.0,
            visibility=16.0,
            transport_wind_speed=15.0,
            transport_wind_direction=225.0,
            mixing_height=1000.0,
            haines_index=2.0,
            lightning_activity_level=0,
            twenty_foot_wind_speed=15.0,
            twenty_foot_wind_direction=225.0,
            wave_height=0.0,
            wave_period=0.0,
            wave_direction=0.0,
            pressure=1015.0,
            temperature_unit="C",
            distance_unit="mi",
            speed_unit="mph",
            precipitation_unit="in",
        ),
        DetailedGridData(
            timestamp=datetime(2024, 1, 15, 14, 0, 0, tzinfo=timezone.utc),
            temperature=5.5,
            dewpoint=1.5,
            max_temperature=6.5,
            min_temperature=4.5,
            relative_humidity=62,
            apparent_temperature=5.0,
            heat_index=5.5,
            wind_chill=4.0,
            sky_cover=30,
            wind_direction=220.0,
            wind_speed=14.0,
            wind_gust=18.0,
            weather_conditions=["Partly Cloudy"],
            probability_of_precipitation=5,
            quantitative_precipitation=0.0,
            ice_accumulation=0.0,
            snowfall_amount=0.0,
            snow_level=0.0,
            ceiling_height=3500.0,
            visibility=15.0,
            transport_wind_speed=14.0,
            transport_wind_direction=220.0,
            mixing_height=1100.0,
            haines_index=2.0,
            lightning_activity_level=0,
            twenty_foot_wind_speed=14.0,
            twenty_foot_wind_direction=220.0,
            wave_height=0.0,
            wave_period=0.0,
            wave_direction=0.0,
            pressure=1016.0,
            temperature_unit="C",
            distance_unit="mi",
            speed_unit="mph",
            precipitation_unit="in",
        ),
    ]


@pytest.fixture
def mock_weather_client(
    mock_config,
    sample_location_search_response,
    sample_current_weather_response,
    sample_forecast_response,
    sample_weather_alerts_response,
    sample_hourly_forecast_response,
    sample_7day_forecast,
    sample_hourly_forecast_objects,
    sample_detailed_grid_data,
):
    """Create a mock NationalWeatherServiceClient with predefined responses"""
    client = AsyncMock(spec=NationalWeatherServiceClient)

    # Mock configuration
    client.config = mock_config

    # Mock context manager methods
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=None)

    # Mock API methods
    client.search_locations = AsyncMock(return_value=sample_location_search_response)
    client.get_location_key = AsyncMock(return_value="40.7128,-74.0060")

    # Mock current weather with proper CurrentWeather object
    mock_current_weather = CurrentWeather(
        temperature=5.0,
        temperature_unit="C",
        humidity=65,
        wind_speed=15.0,
        wind_direction="SW",
        pressure=1015.0,
        visibility=16.0,
        uv_index=2,
        weather_text="Partly Cloudy",
        weather_icon=3,
        precipitation=0.0,
        local_time=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
    )
    client.get_current_weather = AsyncMock(return_value=mock_current_weather)

    # Mock forecast with proper WeatherForecast objects
    mock_forecast = [
        WeatherForecast(
            date=datetime(2024, 1, 15, 7, 0, 0, tzinfo=timezone.utc),
            min_temperature=-2.0,
            max_temperature=5.0,
            temperature_unit="C",
            day_weather_text="Partly Cloudy",
            day_weather_icon=3,
            day_precipitation_probability=0,
            night_weather_text="Clear",
            night_weather_icon=33,
            night_precipitation_probability=0,
        )
    ]
    client.get_5day_forecast = AsyncMock(return_value=mock_forecast)

    # Mock extended forecast methods
    client.get_7day_forecast = AsyncMock(return_value=sample_7day_forecast)
    client.get_daily_forecast = AsyncMock(return_value=sample_7day_forecast)
    client.get_hourly_forecast = AsyncMock(return_value=sample_hourly_forecast_objects)
    client.get_detailed_grid_data = AsyncMock(return_value=sample_detailed_grid_data)

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
            areas=["New York County"],
        )
    ]
    client.get_weather_alerts = AsyncMock(return_value=mock_alerts)

    # Mock other methods
    client.get_indices = AsyncMock(
        return_value={"airquality": {"value": 45, "category": "good"}}
    )
    client.get_historical_weather = AsyncMock(
        return_value=[{"date": "2024-01-10", "temperature": 3.0}]
    )

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
    with patch("main.weather_client", mock_weather_client):
        with patch("weather_mcp.config.get_config", return_value=mock_config):
            yield {"config": mock_config, "weather_client": mock_weather_client}
