"""
National Weather Service API client - completely free alternative to AccuWeather
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

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
class HourlyForecast:
    """Hourly weather forecast information"""

    timestamp: datetime
    temperature: float
    temperature_unit: str
    humidity: int
    wind_speed: float
    wind_direction: str
    wind_gust: float
    pressure: float
    visibility: float
    precipitation_probability: int
    precipitation_amount: float
    weather_text: str
    weather_icon: int
    sky_cover: int
    dewpoint: float
    apparent_temperature: float
    uv_index: int
    is_daytime: bool


@dataclass
class DetailedGridData:
    """Detailed grid forecast data with comprehensive weather parameters"""

    timestamp: datetime
    temperature: float
    dewpoint: float
    max_temperature: float
    min_temperature: float
    relative_humidity: int
    apparent_temperature: float
    heat_index: float
    wind_chill: float
    sky_cover: int
    wind_direction: float
    wind_speed: float
    wind_gust: float
    weather_conditions: list[str]
    probability_of_precipitation: int
    quantitative_precipitation: float
    ice_accumulation: float
    snowfall_amount: float
    snow_level: float
    ceiling_height: float
    visibility: float
    transport_wind_speed: float
    transport_wind_direction: float
    mixing_height: float
    haines_index: float
    lightning_activity_level: int
    twenty_foot_wind_speed: float
    twenty_foot_wind_direction: float
    wave_height: float
    wave_period: float
    wave_direction: float
    pressure: float
    temperature_unit: str
    distance_unit: str
    speed_unit: str
    precipitation_unit: str


@dataclass
class WeatherAlert:
    """Weather alert information"""

    alert_id: str
    title: str
    description: str
    severity: str
    category: str
    start_time: datetime
    end_time: datetime | None
    areas: list[str]


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

    async def _geocode_zip(self, zip_code: str) -> tuple[float, float, str]:
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

    async def _get_grid_point(self, lat: float, lon: float) -> dict[str, Any]:
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
    ) -> list[dict[str, Any]]:
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

    async def get_daily_forecast(
        self, location_key: str, days: int = 5, metric: bool = True
    ) -> list[WeatherForecast]:
        """Get daily weather forecast for specified number of days (up to 7)"""
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
                day_period: dict[str, Any] | None = day_data.get("day")
                night_period: dict[str, Any] | None = day_data.get("night")

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

                # Limit to requested number of days
                if len(forecasts) >= days:
                    break

            return forecasts

        except Exception as e:
            logger.error(f"Error getting forecast for {location_key}: {e}")
            raise

    async def get_5day_forecast(
        self, location_key: str, metric: bool = True
    ) -> list[WeatherForecast]:
        """Get 5-day weather forecast (backward compatibility)"""
        return await self.get_daily_forecast(location_key, days=5, metric=metric)

    async def get_7day_forecast(
        self, location_key: str, metric: bool = True
    ) -> list[WeatherForecast]:
        """Get 7-day weather forecast"""
        return await self.get_daily_forecast(location_key, days=7, metric=metric)

    async def get_hourly_forecast(
        self, location_key: str, hours: int = 168, metric: bool = True
    ) -> list[HourlyForecast]:
        """Get hourly weather forecast for specified number of hours (up to 168 hours/7 days)"""
        try:
            # Parse location key as lat,lon
            lat, lon = map(float, location_key.split(","))

            # Get grid point information
            grid_data = await self._get_grid_point(lat, lon)

            # Get hourly forecast URL
            hourly_forecast_url = grid_data.get("forecastHourly")
            if not hourly_forecast_url:
                raise ValueError("No hourly forecast data available for location")

            # Get the hourly forecast
            response = await self.client.get(hourly_forecast_url)
            response.raise_for_status()

            forecast_data = response.json()
            properties = forecast_data.get("properties", {})
            periods = properties.get("periods", [])

            if not periods:
                raise ValueError("No hourly forecast periods available")

            forecasts = []
            temp_unit = "C" if metric else "F"

            # Process hourly periods
            for period in periods[:hours]:  # Limit to requested hours
                timestamp = datetime.fromisoformat(
                    period["startTime"].replace("Z", "+00:00")
                )

                # Get temperature
                temp = period.get("temperature", 0)
                if metric:
                    temp = (temp - 32) * 5 / 9

                # Get other weather parameters
                humidity = period.get("relativeHumidity", {}).get("value", 0) or 0
                wind_speed = period.get("windSpeed", "0 mph")
                wind_direction = period.get("windDirection", "Unknown")
                wind_gust_str = period.get("windGust", "0 mph")

                # Parse wind speed and gusts
                try:
                    wind_speed_val = float(wind_speed.split()[0]) if wind_speed else 0
                    wind_gust_val = (
                        float(wind_gust_str.split()[0]) if wind_gust_str else 0
                    )
                except (ValueError, IndexError):
                    wind_speed_val = 0
                    wind_gust_val = 0

                # Convert wind speed to metric if requested
                if metric:
                    wind_speed_val = wind_speed_val * 1.60934  # mph to km/h
                    wind_gust_val = wind_gust_val * 1.60934

                # Get precipitation probability
                precip_prob = (
                    period.get("probabilityOfPrecipitation", {}).get("value", 0) or 0
                )

                # Get weather description
                weather_text = period.get("shortForecast", "")

                # Calculate dewpoint (approximation)
                dewpoint = temp - ((100 - humidity) / 5) if humidity > 0 else temp

                hourly_forecast = HourlyForecast(
                    timestamp=timestamp,
                    temperature=round(temp, 1),
                    temperature_unit=temp_unit,
                    humidity=round(humidity),
                    wind_speed=round(wind_speed_val, 1),
                    wind_direction=wind_direction,
                    wind_gust=round(wind_gust_val, 1),
                    pressure=0,  # Not available in hourly forecast
                    visibility=0,  # Not available in hourly forecast
                    precipitation_probability=precip_prob,
                    precipitation_amount=0,  # Not available in hourly forecast
                    weather_text=weather_text,
                    weather_icon=self._text_to_icon(weather_text),
                    sky_cover=0,  # Not available in hourly forecast
                    dewpoint=round(dewpoint, 1),
                    apparent_temperature=round(temp, 1),  # Approximation
                    uv_index=0,  # Not available in hourly forecast
                    is_daytime=period.get("isDaytime", True),
                )
                forecasts.append(hourly_forecast)

            return forecasts

        except Exception as e:
            logger.error(f"Error getting hourly forecast for {location_key}: {e}")
            raise

    async def get_detailed_grid_data(
        self, location_key: str, metric: bool = True
    ) -> list[DetailedGridData]:
        """Get detailed grid forecast data with comprehensive weather parameters"""
        try:
            # Parse location key as lat,lon
            lat, lon = map(float, location_key.split(","))

            # Get grid point information
            grid_data = await self._get_grid_point(lat, lon)

            # Get detailed grid data URL
            grid_data_url = grid_data.get("forecastGridData")
            if not grid_data_url:
                raise ValueError("No detailed grid data available for location")

            # Get the detailed grid data
            response = await self.client.get(grid_data_url)
            response.raise_for_status()

            detailed_data = response.json()
            properties = detailed_data.get("properties", {})

            # Extract time series data
            temp_unit = "C" if metric else "F"
            speed_unit = "km/h" if metric else "mph"
            distance_unit = "km" if metric else "miles"
            precipitation_unit = "mm" if metric else "inches"

            # Get temperature data
            temperature_data = properties.get("temperature", {}).get("values", [])
            dewpoint_data = properties.get("dewpoint", {}).get("values", [])
            humidity_data = properties.get("relativeHumidity", {}).get("values", [])
            wind_speed_data = properties.get("windSpeed", {}).get("values", [])
            wind_direction_data = properties.get("windDirection", {}).get("values", [])
            wind_gust_data = properties.get("windGust", {}).get("values", [])
            sky_cover_data = properties.get("skyCover", {}).get("values", [])
            precip_prob_data = properties.get("probabilityOfPrecipitation", {}).get(
                "values", []
            )
            precip_amount_data = properties.get("quantitativePrecipitation", {}).get(
                "values", []
            )
            visibility_data = properties.get("visibility", {}).get("values", [])
            pressure_data = properties.get("pressure", {}).get("values", [])
            apparent_temp_data = properties.get("apparentTemperature", {}).get(
                "values", []
            )

            # Create a dictionary to merge all data by time
            time_data: dict[datetime, dict[str, Any]] = {}

            # Process temperature data
            for item in temperature_data:
                valid_time = item.get("validTime", "")
                if "/" in valid_time:
                    start_time = valid_time.split("/")[0]
                    timestamp = datetime.fromisoformat(
                        start_time.replace("Z", "+00:00")
                    )
                    temp_c = item.get("value")
                    if temp_c is not None:
                        temp = (temp_c * 9 / 5) + 32 if not metric else temp_c
                        time_data[timestamp] = time_data.get(timestamp, {})
                        time_data[timestamp]["temperature"] = temp

            # Process other data types similarly
            for data_type, data_values in [
                ("dewpoint", dewpoint_data),
                ("humidity", humidity_data),
                ("wind_speed", wind_speed_data),
                ("wind_direction", wind_direction_data),
                ("wind_gust", wind_gust_data),
                ("sky_cover", sky_cover_data),
                ("precip_prob", precip_prob_data),
                ("precip_amount", precip_amount_data),
                ("visibility", visibility_data),
                ("pressure", pressure_data),
                ("apparent_temp", apparent_temp_data),
            ]:
                for item in data_values:
                    valid_time = item.get("validTime", "")
                    if "/" in valid_time:
                        start_time = valid_time.split("/")[0]
                        timestamp = datetime.fromisoformat(
                            start_time.replace("Z", "+00:00")
                        )
                        value = item.get("value")
                        if value is not None:
                            time_data[timestamp] = time_data.get(timestamp, {})
                            time_data[timestamp][data_type] = value

            # Convert to DetailedGridData objects
            detailed_forecasts = []
            for timestamp in sorted(time_data.keys()):
                data = time_data[timestamp]

                temp = data.get("temperature", 0)
                dewpoint = data.get("dewpoint", 0)
                if not metric and dewpoint != 0:
                    dewpoint = (dewpoint * 9 / 5) + 32

                humidity = data.get("humidity", 0)
                wind_speed = data.get("wind_speed", 0)
                wind_direction = data.get("wind_direction", 0)
                wind_gust = data.get("wind_gust", 0)
                sky_cover = data.get("sky_cover", 0)
                precip_prob = data.get("precip_prob", 0)
                precip_amount = data.get("precip_amount", 0)
                visibility = data.get("visibility", 0)
                pressure = data.get("pressure", 0)
                apparent_temp = data.get("apparent_temp", temp)

                # Convert units if needed
                if metric:
                    if wind_speed > 0:
                        wind_speed = wind_speed * 3.6  # m/s to km/h
                    if wind_gust > 0:
                        wind_gust = wind_gust * 3.6
                    if visibility > 0:
                        visibility = visibility / 1000  # meters to kilometers
                    if precip_amount > 0:
                        precip_amount = precip_amount * 1000  # meters to mm
                else:
                    if wind_speed > 0:
                        wind_speed = wind_speed * 2.237  # m/s to mph
                    if wind_gust > 0:
                        wind_gust = wind_gust * 2.237
                    if visibility > 0:
                        visibility = visibility * 0.000621371  # meters to miles
                    if precip_amount > 0:
                        precip_amount = precip_amount * 39.3701  # meters to inches
                    if not metric and apparent_temp != temp:
                        apparent_temp = (apparent_temp * 9 / 5) + 32

                detailed_forecast = DetailedGridData(
                    timestamp=timestamp,
                    temperature=round(temp, 1),
                    dewpoint=round(dewpoint, 1),
                    max_temperature=round(temp, 1),  # Approximation
                    min_temperature=round(temp, 1),  # Approximation
                    relative_humidity=round(humidity),
                    apparent_temperature=round(apparent_temp, 1),
                    heat_index=round(apparent_temp, 1),  # Approximation
                    wind_chill=round(apparent_temp, 1),  # Approximation
                    sky_cover=round(sky_cover),
                    wind_direction=round(wind_direction, 1),
                    wind_speed=round(wind_speed, 1),
                    wind_gust=round(wind_gust, 1),
                    weather_conditions=[],  # Not available in grid data
                    probability_of_precipitation=round(precip_prob),
                    quantitative_precipitation=round(precip_amount, 2),
                    ice_accumulation=0,  # Not available
                    snowfall_amount=0,  # Not available
                    snow_level=0,  # Not available
                    ceiling_height=0,  # Not available
                    visibility=round(visibility, 1),
                    transport_wind_speed=0,  # Not available
                    transport_wind_direction=0,  # Not available
                    mixing_height=0,  # Not available
                    haines_index=0,  # Not available
                    lightning_activity_level=0,  # Not available
                    twenty_foot_wind_speed=0,  # Not available
                    twenty_foot_wind_direction=0,  # Not available
                    wave_height=0,  # Not available
                    wave_period=0,  # Not available
                    wave_direction=0,  # Not available
                    pressure=round(pressure, 1),
                    temperature_unit=temp_unit,
                    distance_unit=distance_unit,
                    speed_unit=speed_unit,
                    precipitation_unit=precipitation_unit,
                )
                detailed_forecasts.append(detailed_forecast)

            return detailed_forecasts

        except Exception as e:
            logger.error(f"Error getting detailed grid data for {location_key}: {e}")
            raise

    async def get_weather_alerts(self, location_key: str) -> list[WeatherAlert]:
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
