"""
Pydantic models for Weather MCP Server
"""

from pydantic import BaseModel, Field


class LocationQuery(BaseModel):
    """Location search query"""

    query: str = Field(..., description="Location name or ZIP code to search for")
    language: str = Field("en-us", description="Language code for results")


class LocationKey(BaseModel):
    """Location key for weather data"""

    location_key: str = Field(..., description="Location identifier (lat,lon format)")
    details: bool = Field(True, description="Include detailed weather information")


class ForecastQuery(BaseModel):
    """Forecast query parameters"""

    location_key: str = Field(..., description="Location identifier (lat,lon format)")
    metric: bool = Field(True, description="Use metric units (Celsius)")


class ExtendedForecastQuery(BaseModel):
    """Extended forecast query parameters"""

    location_key: str = Field(..., description="Location identifier (lat,lon format)")
    days: int = Field(7, description="Number of days for forecast (up to 7)")
    metric: bool = Field(True, description="Use metric units (Celsius)")


class HourlyForecastQuery(BaseModel):
    """Hourly forecast query parameters"""

    location_key: str = Field(..., description="Location identifier (lat,lon format)")
    hours: int = Field(
        168, description="Number of hours for forecast (up to 168 hours/7 days)"
    )
    metric: bool = Field(True, description="Use metric units (Celsius)")
