"""
AccuWeather API client for weather data retrieval
"""

import asyncio
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from cachetools import TTLCache
import httpx
from loguru import logger

from .config import Config


@dataclass
class WeatherAlert:
    """Weather alert data structure"""
    alert_id: str
    title: str
    description: str
    severity: str
    category: str
    start_time: datetime
    end_time: Optional[datetime]
    areas: List[str]


@dataclass
class CurrentWeather:
    """Current weather data structure"""
    location_key: str
    location_name: str
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
    """Weather forecast data structure"""
    date: datetime
    day_temperature: float
    night_temperature: float
    day_weather_text: str
    night_weather_text: str
    day_icon: int
    night_icon: int
    precipitation_probability: int
    precipitation_amount: float
    wind_speed: float
    wind_direction: str


class AccuWeatherClient:
    """AccuWeather API client with caching and rate limiting"""
    
    def __init__(self, config: Config):
        self.config = config
        self.base_url = config.accuweather_base_url
        self.api_key = config.accuweather_api_key
        
        # Rate limiting (AccuWeather has limits on free tier)
        self._last_request_time = 0
        self._min_request_interval = 1.0  # 1 second between requests
        
        # Caching
        self._cache = TTLCache(
            maxsize=config.cache_max_size,
            ttl=config.cache_ttl_seconds
        )
        
        # HTTP client
        self._client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Clima-MCP/1.0.0"
            }
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make rate-limited request to AccuWeather API"""
        
        # Check if client is closed and recreate if needed
        if self._client.is_closed:
            logger.warning("HTTP client was closed, recreating...")
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={
                    "User-Agent": "Clima-MCP/1.0.0"
                }
            )
        
        # Rate limiting
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self._min_request_interval:
            await asyncio.sleep(self._min_request_interval - time_since_last)
        
        # Add API key to params
        params["apikey"] = self.api_key
        
        # Build URL
        url = f"{self.base_url}{endpoint}"
        
        # Check cache first
        cache_key = f"{endpoint}:{str(sorted(params.items()))}"
        if cache_key in self._cache:
            logger.debug(f"Cache hit for {endpoint}")
            return self._cache[cache_key]
        
        try:
            logger.debug(f"Making request to {endpoint} with params: {params}")
            response = await self._client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache successful responses
            self._cache[cache_key] = data
            self._last_request_time = time.time()
            
            logger.debug(f"Successful response from {endpoint}")
            return data
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {endpoint}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            raise
    
    async def search_locations(self, query: str, language: str = "en-us") -> List[Dict[str, Any]]:
        """Search for locations by name"""
        params = {
            "q": query,
            "language": language
        }
        return await self._make_request("/locations/v1/cities/search", params)
    
    async def get_location_key(self, lat: float, lon: float) -> str:
        """Get location key for coordinates"""
        params = {
            "q": f"{lat},{lon}"
        }
        result = await self._make_request("/locations/v1/cities/geoposition/search", params)
        return result["Key"]
    
    async def get_current_weather(self, location_key: str, details: bool = True) -> CurrentWeather:
        """Get current weather conditions"""
        params = {
            "details": str(details).lower()
        }
        
        data = await self._make_request(f"/currentconditions/v1/{location_key}", params)
        
        if not data:
            raise ValueError(f"No current weather data for location {location_key}")
        
        current = data[0]
        
        return CurrentWeather(
            location_key=location_key,
            location_name="",  # Will be filled by location lookup if needed
            temperature=current["Temperature"]["Metric"]["Value"],
            temperature_unit=current["Temperature"]["Metric"]["Unit"],
            humidity=current.get("RelativeHumidity", 0),
            wind_speed=current.get("Wind", {}).get("Speed", {}).get("Metric", {}).get("Value", 0),
            wind_direction=current.get("Wind", {}).get("Direction", {}).get("English", ""),
            pressure=current.get("Pressure", {}).get("Metric", {}).get("Value", 0),
            visibility=current.get("Visibility", {}).get("Metric", {}).get("Value", 0),
            uv_index=current.get("UVIndex", 0),
            weather_text=current.get("WeatherText", ""),
            weather_icon=current.get("WeatherIcon", 0),
            precipitation=current.get("PrecipitationSummary", {}).get("Precipitation", {}).get("Metric", {}).get("Value", 0),
            local_time=datetime.fromisoformat(current["LocalObservationDateTime"].replace("Z", "+00:00"))
        )
    
    async def get_5day_forecast(self, location_key: str, metric: bool = True) -> List[WeatherForecast]:
        """Get 5-day weather forecast"""
        params = {
            "metric": str(metric).lower()
        }
        
        data = await self._make_request(f"/forecasts/v1/daily/5day/{location_key}", params)
        forecasts = []
        
        for daily in data["DailyForecasts"]:
            forecast = WeatherForecast(
                date=datetime.fromisoformat(daily["Date"].replace("Z", "+00:00")),
                day_temperature=daily["Temperature"]["Maximum"]["Value"],
                night_temperature=daily["Temperature"]["Minimum"]["Value"],
                day_weather_text=daily["Day"]["IconPhrase"],
                night_weather_text=daily["Night"]["IconPhrase"],
                day_icon=daily["Day"]["Icon"],
                night_icon=daily["Night"]["Icon"],
                precipitation_probability=daily["Day"]["PrecipitationProbability"],
                precipitation_amount=0,  # Not available in basic forecast
                wind_speed=daily["Day"]["Wind"]["Speed"]["Value"],
                wind_direction=daily["Day"]["Wind"]["Direction"]["English"]
            )
            forecasts.append(forecast)
        
        return forecasts
    
    async def get_hourly_forecast(self, location_key: str, hours: int = 12) -> List[Dict[str, Any]]:
        """Get hourly weather forecast"""
        if hours not in [1, 12, 24, 72, 120]:
            hours = 12  # Default to 12 hours
        
        data = await self._make_request(f"/forecasts/v1/hourly/{hours}hour/{location_key}", {})
        return data
    
    async def get_weather_alerts(self, location_key: str) -> List[WeatherAlert]:
        """Get weather alerts for location"""
        try:
            data = await self._make_request(f"/alerts/v1/{location_key}", {})
            alerts = []
            
            for alert in data:
                weather_alert = WeatherAlert(
                    alert_id=str(alert.get("AlertID", "")),
                    title=alert.get("Headline", {}).get("Text", ""),
                    description=alert.get("Description", {}).get("Text", ""),
                    severity=alert.get("Level", ""),
                    category=alert.get("Category", ""),
                    start_time=datetime.fromisoformat(alert["EffectiveDate"].replace("Z", "+00:00")),
                    end_time=datetime.fromisoformat(alert["ExpireDate"].replace("Z", "+00:00")) if alert.get("ExpireDate") else None,
                    areas=alert.get("Areas", [])
                )
                alerts.append(weather_alert)
            
            return alerts
            
        except Exception as e:
            logger.warning(f"Failed to get weather alerts for {location_key}: {e}")
            return []
    
    async def get_indices(self, location_key: str, index_id: int = 1) -> Dict[str, Any]:
        """Get weather indices (e.g., air quality, UV index)"""
        try:
            data = await self._make_request(f"/indices/v1/daily/1day/{location_key}/{index_id}", {})
            return data[0] if data else {}
        except Exception as e:
            logger.warning(f"Failed to get indices for {location_key}: {e}")
            return {}
    
    async def get_historical_weather(self, location_key: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get historical weather data (requires premium API access)"""
        params = {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        }
        
        try:
            data = await self._make_request(f"/currentconditions/v1/{location_key}/historical", params)
            return data
        except Exception as e:
            logger.warning(f"Failed to get historical weather for {location_key}: {e}")
            return [] 