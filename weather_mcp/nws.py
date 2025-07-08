"""
National Weather Service API client - completely free alternative to AccuWeather
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import httpx
from loguru import logger


@dataclass
class WeatherLocation:
    """Weather location information"""

    key: str  # We'll use lat,lon as key for NWS
    name: str
    region: str
    country: str
    latitude: float
    longitude: float


@dataclass
class CurrentWeather:
    """Current weather conditions"""

    temperature: float
    temperature_unit: str
    humidity: int
    wind_speed: float
    wind_direction: str
    pressure: float
    visibility: float
    uv_index: int
    weather_text: str
    weather_icon: int
    precipitation: float
    local_time: datetime


@dataclass
class WeatherForecast:
    """Weather forecast information"""

    date: datetime
    min_temperature: float
    max_temperature: float
    temperature_unit: str
    day_weather_text: str
    day_weather_icon: int
    day_precipitation_probability: int
    night_weather_text: str
    night_weather_icon: int
    night_precipitation_probability: int


@dataclass
class WeatherAlert:
    """Weather alert information"""

    alert_id: str
    title: str
    description: str
    severity: str
    category: str
    start_time: datetime
    end_time: Optional[datetime]
    areas: List[str]


class NationalWeatherServiceClient:
    """National Weather Service API client - completely free!"""

    def __init__(self):
        self.base_url = "https://api.weather.gov"
        self.geocoding_url = "https://nominatim.openstreetmap.org"
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "WeatherMCP/1.0.0 (https://github.com/Kode-Rex/clima)"
            },
        )
        # Grid point cache to avoid repeated lookups
        self._grid_cache = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    async def _geocode_zip(self, zip_code: str) -> Tuple[float, float, str]:
        """Convert zip code to coordinates using OpenStreetMap Nominatim"""
        try:
            # Use Nominatim to get coordinates for US zip code
            url = f"{self.geocoding_url}/search"
            params = {
                "q": f"{zip_code}, USA",
                "format": "json",
                "limit": 1,
                "countrycodes": "us",
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            if not data:
                raise ValueError(f"No location found for zip code {zip_code}")

            location = data[0]
            lat = float(location["lat"])
            lon = float(location["lon"])
            name = location.get("display_name", f"ZIP {zip_code}")

            # Clean up the name to be more readable
            name_parts = name.split(", ")
            if len(name_parts) >= 2:
                name = f"{name_parts[0]}, {name_parts[1]}"

            logger.info(f"Geocoded {zip_code} to {lat}, {lon} ({name})")
            return lat, lon, name

        except Exception as e:
            logger.error(f"Error geocoding zip code {zip_code}: {e}")
            raise

    async def _get_grid_point(self, lat: float, lon: float) -> Dict[str, Any]:
        """Get NWS grid point information for coordinates"""
        cache_key = f"{lat:.4f},{lon:.4f}"
        if cache_key in self._grid_cache:
            return self._grid_cache[cache_key]

        try:
            url = f"{self.base_url}/points/{lat:.4f},{lon:.4f}"
            response = await self.client.get(url)
            response.raise_for_status()

            data = response.json()
            properties = data.get("properties", {})

            if not properties:
                raise ValueError(f"No grid point data for coordinates {lat}, {lon}")

            self._grid_cache[cache_key] = properties
            logger.debug(f"Retrieved grid point data for {lat}, {lon}")
            return properties

        except Exception as e:
            logger.error(f"Error getting grid point for {lat}, {lon}: {e}")
            raise

    async def search_locations(
        self, query: str, language: str = "en-us"
    ) -> List[Dict[str, Any]]:
        """Search for locations by name or zip code"""
        try:
            # Check if query looks like a zip code
            if query.isdigit() and len(query) == 5:
                lat, lon, name = await self._geocode_zip(query)
                return [
                    {
                        "Key": f"{lat:.4f},{lon:.4f}",
                        "LocalizedName": name,
                        "Region": {"LocalizedName": "United States"},
                        "Country": {"LocalizedName": "United States"},
                        "GeoPosition": {"Latitude": lat, "Longitude": lon},
                    }
                ]
            else:
                # Search by name using Nominatim
                url = f"{self.geocoding_url}/search"
                params = {
                    "q": f"{query}, USA",
                    "format": "json",
                    "limit": 10,
                    "countrycodes": "us",
                }

                response = await self.client.get(url, params=params)
                response.raise_for_status()

                data = response.json()
                locations = []

                for location in data:
                    lat = float(location["lat"])
                    lon = float(location["lon"])
                    name = location.get("display_name", "Unknown Location")

                    # Clean up the name
                    name_parts = name.split(", ")
                    if len(name_parts) >= 2:
                        name = f"{name_parts[0]}, {name_parts[1]}"

                    locations.append(
                        {
                            "Key": f"{lat:.4f},{lon:.4f}",
                            "LocalizedName": name,
                            "Region": {"LocalizedName": "United States"},
                            "Country": {"LocalizedName": "United States"},
                            "GeoPosition": {"Latitude": lat, "Longitude": lon},
                        }
                    )

                return locations

        except Exception as e:
            logger.error(f"Error searching locations for '{query}': {e}")
            return []

    async def get_current_weather(
        self, location_key: str, details: bool = True
    ) -> CurrentWeather:
        """Get current weather conditions"""
        try:
            # Parse location key as lat,lon
            lat, lon = map(float, location_key.split(","))

            # Get grid point information
            grid_data = await self._get_grid_point(lat, lon)

            # Get current conditions from the nearest observation station
            stations_url = grid_data.get("observationStations")
            if not stations_url:
                raise ValueError("No observation stations found for location")

            # Get the list of stations
            response = await self.client.get(stations_url)
            response.raise_for_status()
            stations_data = response.json()

            stations = stations_data.get("features", [])
            if not stations:
                raise ValueError("No observation stations available")

            # Try to get current conditions from the first few stations
            for station in stations[:3]:  # Try first 3 stations
                try:
                    station_id = station["properties"]["stationIdentifier"]
                    obs_url = (
                        f"{self.base_url}/stations/{station_id}/observations/latest"
                    )

                    response = await self.client.get(obs_url)
                    response.raise_for_status()

                    obs_data = response.json()
                    properties = obs_data.get("properties", {})

                    if not properties:
                        continue

                    # Extract weather data
                    temp_c = properties.get("temperature", {}).get("value")
                    if temp_c is None:
                        continue

                    temp_f = (temp_c * 9 / 5) + 32 if temp_c is not None else 0

                    humidity = properties.get("relativeHumidity", {}).get("value", 0)
                    wind_speed_ms = properties.get("windSpeed", {}).get("value", 0)
                    wind_speed_mph = wind_speed_ms * 2.237 if wind_speed_ms else 0
                    wind_direction = properties.get("windDirection", {}).get("value", 0)

                    # Convert wind direction to compass
                    wind_dir_text = self._degrees_to_compass(wind_direction)

                    pressure_pa = properties.get("barometricPressure", {}).get(
                        "value", 0
                    )
                    pressure_inhg = pressure_pa * 0.0002953 if pressure_pa else 0

                    visibility_m = properties.get("visibility", {}).get("value", 0)
                    visibility_mi = visibility_m * 0.000621371 if visibility_m else 0

                    weather_text = properties.get("textDescription", "Clear")

                    # Get precipitation (if available)
                    precip_m = properties.get("precipitationLastHour", {}).get(
                        "value", 0
                    )
                    precip_in = precip_m * 39.3701 if precip_m else 0

                    # Get observation time
                    obs_time_str = properties.get(
                        "timestamp", datetime.now().isoformat()
                    )
                    obs_time = datetime.fromisoformat(
                        obs_time_str.replace("Z", "+00:00")
                    )

                    return CurrentWeather(
                        temperature=round(temp_f, 1),
                        temperature_unit="F",
                        humidity=round(humidity) if humidity else 0,
                        wind_speed=round(wind_speed_mph, 1),
                        wind_direction=wind_dir_text,
                        pressure=round(pressure_inhg, 2),
                        visibility=round(visibility_mi, 1),
                        uv_index=0,  # NWS doesn't provide UV index in observations
                        weather_text=weather_text,
                        weather_icon=self._text_to_icon(weather_text),
                        precipitation=round(precip_in, 2),
                        local_time=obs_time,
                    )

                except Exception as station_error:
                    logger.debug(
                        f"Station {station.get('properties', {}).get('stationIdentifier', 'unknown')} failed: {station_error}"
                    )
                    continue

            raise ValueError("No current weather data available from any station")

        except Exception as e:
            logger.error(f"Error getting current weather for {location_key}: {e}")
            raise

    async def get_5day_forecast(
        self, location_key: str, metric: bool = True
    ) -> List[WeatherForecast]:
        """Get 5-day weather forecast"""
        try:
            # Parse location key as lat,lon
            lat, lon = map(float, location_key.split(","))

            # Get grid point information
            grid_data = await self._get_grid_point(lat, lon)

            # Get forecast URL
            forecast_url = grid_data.get("forecast")
            if not forecast_url:
                raise ValueError("No forecast data available for location")

            # Get the forecast
            response = await self.client.get(forecast_url)
            response.raise_for_status()

            forecast_data = response.json()
            properties = forecast_data.get("properties", {})
            periods = properties.get("periods", [])

            if not periods:
                raise ValueError("No forecast periods available")

            forecasts = []
            temp_unit = "C" if metric else "F"

            # Group periods by day (day/night pairs)
            day_periods = {}
            for period in periods:
                date = datetime.fromisoformat(
                    period["startTime"].replace("Z", "+00:00")
                ).date()
                if date not in day_periods:
                    day_periods[date] = {"day": None, "night": None}

                if period["isDaytime"]:
                    day_periods[date]["day"] = period
                else:
                    day_periods[date]["night"] = period

            # Create forecast objects
            for date, day_data in sorted(day_periods.items()):
                day_period: Optional[Dict[str, Any]] = day_data.get("day")
                night_period: Optional[Dict[str, Any]] = day_data.get("night")

                # Skip if we don't have at least day data
                if not day_period:
                    continue

                # Ensure we have valid dictionaries
                if day_period is None:
                    day_period = {}
                if night_period is None:
                    night_period = {}

                # Get temperatures
                day_temp = day_period.get("temperature", 0)
                night_temp = (
                    night_period.get("temperature", 0)
                    if night_period
                    else day_temp - 10
                )

                # Convert to Celsius if requested
                if metric:
                    day_temp = (day_temp - 32) * 5 / 9
                    night_temp = (night_temp - 32) * 5 / 9

                # Determine min/max
                min_temp = min(day_temp, night_temp)
                max_temp = max(day_temp, night_temp)

                forecast = WeatherForecast(
                    date=datetime.combine(date, datetime.min.time()),
                    min_temperature=round(min_temp, 1),
                    max_temperature=round(max_temp, 1),
                    temperature_unit=temp_unit,
                    day_weather_text=day_period.get("shortForecast", ""),
                    day_weather_icon=self._text_to_icon(
                        day_period.get("shortForecast", "")
                    ),
                    day_precipitation_probability=day_period.get(
                        "probabilityOfPrecipitation", {}
                    ).get("value", 0)
                    or 0,
                    night_weather_text=(
                        night_period.get("shortForecast", "") if night_period else ""
                    ),
                    night_weather_icon=(
                        self._text_to_icon(night_period.get("shortForecast", ""))
                        if night_period
                        else 0
                    ),
                    night_precipitation_probability=(
                        night_period.get("probabilityOfPrecipitation", {}).get(
                            "value", 0
                        )
                        or 0
                        if night_period
                        else 0
                    ),
                )
                forecasts.append(forecast)

                # Limit to 5 days
                if len(forecasts) >= 5:
                    break

            return forecasts

        except Exception as e:
            logger.error(f"Error getting forecast for {location_key}: {e}")
            raise

    async def get_weather_alerts(self, location_key: str) -> List[WeatherAlert]:
        """Get weather alerts for location"""
        try:
            # Parse location key as lat,lon
            lat, lon = map(float, location_key.split(","))

            # Get active alerts for this point
            url = f"{self.base_url}/alerts/active"
            params = {
                "point": f"{lat:.4f},{lon:.4f}",
                "status": "actual",
                "message_type": "alert",
            }

            response = await self.client.get(url, params=params)
            response.raise_for_status()

            data = response.json()
            alerts = []

            for feature in data.get("features", []):
                properties = feature.get("properties", {})

                # Parse alert data
                alert_id = properties.get("id", "")
                title = properties.get("headline", "Weather Alert")
                description = properties.get("description", "")
                severity = properties.get("severity", "Unknown").title()
                category = properties.get("category", "Weather").title()

                # Parse times
                start_time = datetime.fromisoformat(
                    properties.get("onset", "").replace("Z", "+00:00")
                )
                end_time = None
                if properties.get("expires"):
                    end_time = datetime.fromisoformat(
                        properties.get("expires", "").replace("Z", "+00:00")
                    )

                # Parse areas
                areas = []
                area_desc = properties.get("areaDesc", "")
                if area_desc:
                    areas = [area.strip() for area in area_desc.split(";")]

                alert = WeatherAlert(
                    alert_id=alert_id,
                    title=title,
                    description=description,
                    severity=severity,
                    category=category,
                    start_time=start_time,
                    end_time=end_time,
                    areas=areas,
                )
                alerts.append(alert)

            logger.info(f"Retrieved {len(alerts)} NWS alerts for {location_key}")
            return alerts

        except Exception as e:
            logger.error(f"Error fetching NWS alerts for {location_key}: {e}")
            return []

    def _degrees_to_compass(self, degrees: float) -> str:
        """Convert wind direction degrees to compass direction"""
        if degrees is None:
            return "Unknown"

        directions = [
            "N",
            "NNE",
            "NE",
            "ENE",
            "E",
            "ESE",
            "SE",
            "SSE",
            "S",
            "SSW",
            "SW",
            "WSW",
            "W",
            "WNW",
            "NW",
            "NNW",
        ]

        index = round(degrees / 22.5) % 16
        return directions[index]

    def _text_to_icon(self, weather_text: str) -> int:
        """Convert weather description to icon number (rough mapping)"""
        if not weather_text:
            return 1

        text_lower = weather_text.lower()

        # Map common weather descriptions to icon numbers
        if "clear" in text_lower or "sunny" in text_lower:
            return 1
        elif "partly cloudy" in text_lower or "partly sunny" in text_lower:
            return 3
        elif "cloudy" in text_lower or "overcast" in text_lower:
            return 7
        elif "rain" in text_lower or "shower" in text_lower:
            return 18
        elif "thunderstorm" in text_lower or "storm" in text_lower:
            return 15
        elif "snow" in text_lower:
            return 22
        elif "fog" in text_lower or "mist" in text_lower:
            return 11
        elif "wind" in text_lower:
            return 24
        else:
            return 1  # Default to clear
