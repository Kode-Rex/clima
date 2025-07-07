"""
Weather SSE (Server-Sent Events) implementation using National Weather Service API
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Set, List, Optional
from dataclasses import dataclass
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from .config import Config
from .nws import NationalWeatherServiceClient, WeatherAlert


@dataclass
class SSEConnection:
    """SSE connection tracking"""
    id: str
    location_key: str
    zip_code: str
    location_name: str
    created_at: datetime
    last_heartbeat: datetime
    alert_types: Set[str]
    
    def is_expired(self, timeout_seconds: int = 300) -> bool:
        """Check if connection has expired"""
        return (datetime.now() - self.last_heartbeat).total_seconds() > timeout_seconds


class WeatherSSEManager:
    """Manages SSE connections for weather updates"""
    
    def __init__(self, config: Config, weather_client: NationalWeatherServiceClient):
        self.config = config
        self.weather_client = weather_client
        self.connections: Dict[str, SSEConnection] = {}
        self.location_subscribers: Dict[str, Set[str]] = {}  # location_key -> connection_ids
        self.alert_cache: Dict[str, List[WeatherAlert]] = {}  # location_key -> alerts
        self.running = False
        
        # Background tasks
        self._heartbeat_task: Optional[asyncio.Task] = None
        self._alert_monitor_task: Optional[asyncio.Task] = None
        
        logger.info("Weather SSE Manager initialized")
    
    async def start(self):
        """Start background tasks for SSE management"""
        if self.running:
            return
        
        self.running = True
        self._heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._alert_monitor_task = asyncio.create_task(self._alert_monitor_loop())
        
        logger.info("Weather SSE Manager started")
    
    async def stop(self):
        """Stop background tasks"""
        self.running = False
        
        if self._heartbeat_task:
            self._heartbeat_task.cancel()
        if self._alert_monitor_task:
            self._alert_monitor_task.cancel()
        
        # Wait for tasks to complete
        tasks = [t for t in [self._heartbeat_task, self._alert_monitor_task] if t]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        logger.info("Weather SSE Manager stopped")
    
    async def _zip_to_location_key(self, zip_code: str) -> tuple[str, str]:
        """Convert zip code to location key and name using NWS geocoding"""
        try:
            # Use NWS client to search for location
            locations = await self.weather_client.search_locations(zip_code)
            
            if not locations:
                raise ValueError(f"No location found for zip code {zip_code}")
            
            location = locations[0]
            location_key = location["Key"]  # This will be "lat,lon" format
            location_name = location["LocalizedName"]
            
            logger.info(f"Converted zip code {zip_code} to location: {location_name} (Key: {location_key})")
            return location_key, location_name
            
        except Exception as e:
            logger.error(f"Error converting zip code {zip_code} to location: {e}")
            raise

    def add_connection(self, connection_id: str, location_key: str, zip_code: str = "", location_name: str = "", alert_types: Set[str] = None) -> SSEConnection:
        """Add a new SSE connection"""
        if alert_types is None:
            alert_types = {"all"}
        
        connection = SSEConnection(
            id=connection_id,
            location_key=location_key,
            zip_code=zip_code,
            location_name=location_name,
            created_at=datetime.now(),
            last_heartbeat=datetime.now(),
            alert_types=alert_types
        )
        
        self.connections[connection_id] = connection
        
        # Add to location subscribers
        if location_key not in self.location_subscribers:
            self.location_subscribers[location_key] = set()
        self.location_subscribers[location_key].add(connection_id)
        
        logger.info(f"Added SSE connection {connection_id} for {location_name or zip_code} (location key: {location_key})")
        return connection
    
    def remove_connection(self, connection_id: str):
        """Remove an SSE connection"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        location_key = connection.location_key
        
        # Remove from connections
        del self.connections[connection_id]
        
        # Remove from location subscribers
        if location_key in self.location_subscribers:
            self.location_subscribers[location_key].discard(connection_id)
            if not self.location_subscribers[location_key]:
                del self.location_subscribers[location_key]
        
        logger.info(f"Removed SSE connection {connection_id}")
    
    def update_heartbeat(self, connection_id: str):
        """Update connection heartbeat"""
        if connection_id in self.connections:
            self.connections[connection_id].last_heartbeat = datetime.now()
    
    async def _heartbeat_loop(self):
        """Background task to send heartbeat and clean expired connections"""
        while self.running:
            try:
                await asyncio.sleep(self.config.sse_heartbeat_interval)
                
                current_time = datetime.now()
                expired_connections = []
                
                for connection_id, connection in self.connections.items():
                    # Increase timeout to 5 minutes (300 seconds) instead of 90 seconds
                    if connection.is_expired(300):
                        expired_connections.append(connection_id)
                
                # Remove expired connections
                for connection_id in expired_connections:
                    self.remove_connection(connection_id)
                    logger.info(f"Removed expired connection {connection_id}")
                
                # Log heartbeat status
                if self.connections:
                    logger.debug(f"Heartbeat check: {len(self.connections)} active connections")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
    
    async def _alert_monitor_loop(self):
        """Background task to monitor weather alerts"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                if not self.location_subscribers:
                    continue
                
                # Check alerts for all subscribed locations
                for location_key in self.location_subscribers.keys():
                    try:
                        current_alerts = await self.weather_client.get_weather_alerts(location_key)
                        cached_alerts = self.alert_cache.get(location_key, [])
                        
                        # Find new alerts
                        new_alerts = []
                        cached_alert_ids = {alert.alert_id for alert in cached_alerts}
                        
                        for alert in current_alerts:
                            if alert.alert_id not in cached_alert_ids:
                                new_alerts.append(alert)
                        
                        # Update cache
                        self.alert_cache[location_key] = current_alerts
                        
                        # Send new alerts to subscribers
                        if new_alerts:
                            await self._broadcast_alerts(location_key, new_alerts)
                        
                    except Exception as e:
                        logger.error(f"Error checking alerts for location {location_key}: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in alert monitor loop: {e}")
    
    async def _broadcast_alerts(self, location_key: str, alerts: List[WeatherAlert]):
        """Broadcast weather alerts to subscribers"""
        if location_key not in self.location_subscribers:
            return
        
        subscriber_ids = self.location_subscribers[location_key].copy()
        
        for connection_id in subscriber_ids:
            connection = self.connections.get(connection_id)
            if not connection:
                continue
            
            # Filter alerts based on connection's alert types
            filtered_alerts = []
            for alert in alerts:
                if "all" in connection.alert_types or alert.category.lower() in connection.alert_types:
                    filtered_alerts.append(alert)
            
            if filtered_alerts:
                alert_data = {
                    "type": "weather_alert",
                    "location_key": location_key,
                    "timestamp": datetime.now().isoformat(),
                    "alerts": [
                        {
                            "alert_id": alert.alert_id,
                            "title": alert.title,
                            "description": alert.description,
                            "severity": alert.severity,
                            "category": alert.category,
                            "start_time": alert.start_time.isoformat(),
                            "end_time": alert.end_time.isoformat() if alert.end_time else None,
                            "areas": alert.areas
                        }
                        for alert in filtered_alerts
                    ]
                }
                
                # In a real implementation, we'd send this to the specific connection
                logger.info(f"Broadcasting {len(filtered_alerts)} alerts to connection {connection_id}")
    
    async def get_current_weather_stream(self, location_key: str, connection_id: str):
        """Generate SSE stream for current weather updates"""
        connection = self.connections.get(connection_id)
        if not connection:
            raise ValueError(f"Connection {connection_id} not found")
        
        async def event_generator():
            # Send immediate weather update on connection
            try:
                # Get current weather immediately
                weather = await self.weather_client.get_current_weather(location_key)
                
                # Update heartbeat
                self.update_heartbeat(connection_id)
                
                # Prepare weather data with location info
                weather_data = {
                    "type": "current_weather",
                    "location_key": location_key,
                    "zip_code": connection.zip_code,
                    "location_name": connection.location_name,
                    "timestamp": datetime.now().isoformat(),
                    "weather": {
                        "temperature": weather.temperature,
                        "temperature_unit": weather.temperature_unit,
                        "humidity": weather.humidity,
                        "wind_speed": weather.wind_speed,
                        "wind_direction": weather.wind_direction,
                        "pressure": weather.pressure,
                        "visibility": weather.visibility,
                        "uv_index": weather.uv_index,
                        "weather_text": weather.weather_text,
                        "weather_icon": weather.weather_icon,
                        "precipitation": weather.precipitation,
                        "local_time": weather.local_time.isoformat()
                    }
                }
                
                # Send weather update in SSE format
                yield f"event: weather_update\ndata: {json.dumps(weather_data)}\n\n"
                
                logger.info(f"Sent initial weather data to connection {connection_id}")
                
                # Check for current alerts immediately
                try:
                    current_alerts = await self.weather_client.get_weather_alerts(location_key)
                    if current_alerts:
                        # Filter alerts based on connection's alert types
                        filtered_alerts = []
                        for alert in current_alerts:
                            if "all" in connection.alert_types or alert.category.lower() in connection.alert_types:
                                filtered_alerts.append(alert)
                        
                        if filtered_alerts:
                            alert_data = {
                                "type": "weather_alert",
                                "location_key": location_key,
                                "zip_code": connection.zip_code,
                                "location_name": connection.location_name,
                                "timestamp": datetime.now().isoformat(),
                                "alerts": [
                                    {
                                        "alert_id": alert.alert_id,
                                        "title": alert.title,
                                        "description": alert.description,
                                        "severity": alert.severity,
                                        "category": alert.category,
                                        "start_time": alert.start_time.isoformat(),
                                        "end_time": alert.end_time.isoformat() if alert.end_time else None,
                                        "areas": alert.areas
                                    }
                                    for alert in filtered_alerts
                                ]
                            }
                            
                            yield f"event: weather_alert\ndata: {json.dumps(alert_data)}\n\n"
                            
                            logger.info(f"Sent {len(filtered_alerts)} immediate alerts to connection {connection_id}")
                            
                            # Send status update about successful alert retrieval
                            alert_success = {
                                "type": "alert_status",
                                "location_key": location_key,
                                "zip_code": connection.zip_code,
                                "location_name": connection.location_name,
                                "timestamp": datetime.now().isoformat(),
                                "message": f"Successfully retrieved {len(filtered_alerts)} weather alerts from National Weather Service",
                                "status": "success"
                            }
                            
                            yield f"event: alert_status\ndata: {json.dumps(alert_success)}\n\n"
                        
                        # Cache the alerts
                        self.alert_cache[location_key] = current_alerts
                        
                except Exception as e:
                    # Handle any alert errors gracefully
                    logger.warning(f"Could not check alerts for {location_key}: {e}")
                    
                    # Send info about no alerts available
                    alert_info = {
                        "type": "alert_status",
                        "location_key": location_key,
                        "zip_code": connection.zip_code,
                        "location_name": connection.location_name,
                        "timestamp": datetime.now().isoformat(),
                        "message": f"No weather alerts available for this location",
                        "status": "info"
                    }
                    
                    yield f"event: alert_status\ndata: {json.dumps(alert_info)}\n\n"
                
            except Exception as e:
                logger.error(f"Error sending initial weather data to {connection_id}: {e}")
                error_data = {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
            
            # Continue with periodic updates
            last_weather_update = datetime.now()
            last_alert_check = datetime.now()
            
            while self.running and connection_id in self.connections:
                try:
                    current_time = datetime.now()
                    
                    # Send heartbeat every 30 seconds
                    heartbeat_data = {
                        "type": "heartbeat",
                        "timestamp": current_time.isoformat(),
                        "connection_id": connection_id
                    }
                    
                    yield f"event: heartbeat\ndata: {json.dumps(heartbeat_data)}\n\n"
                    
                    # Update heartbeat timestamp
                    self.update_heartbeat(connection_id)
                    
                    # Check for new alerts every 60 seconds
                    if (current_time - last_alert_check).total_seconds() >= 60:
                        try:
                            current_alerts = await self.weather_client.get_weather_alerts(location_key)
                            cached_alerts = self.alert_cache.get(location_key, [])
                            
                            # Find new alerts
                            new_alerts = []
                            cached_alert_ids = {alert.alert_id for alert in cached_alerts}
                            
                            for alert in current_alerts:
                                if alert.alert_id not in cached_alert_ids:
                                    new_alerts.append(alert)
                            
                            # Update cache
                            self.alert_cache[location_key] = current_alerts
                            
                            # Send new alerts
                            if new_alerts:
                                # Filter alerts based on connection's alert types
                                filtered_alerts = []
                                for alert in new_alerts:
                                    if "all" in connection.alert_types or alert.category.lower() in connection.alert_types:
                                        filtered_alerts.append(alert)
                                
                                if filtered_alerts:
                                    alert_data = {
                                        "type": "weather_alert",
                                        "location_key": location_key,
                                        "zip_code": connection.zip_code,
                                        "location_name": connection.location_name,
                                        "timestamp": current_time.isoformat(),
                                        "alerts": [
                                            {
                                                "alert_id": alert.alert_id,
                                                "title": alert.title,
                                                "description": alert.description,
                                                "severity": alert.severity,
                                                "category": alert.category,
                                                "start_time": alert.start_time.isoformat(),
                                                "end_time": alert.end_time.isoformat() if alert.end_time else None,
                                                "areas": alert.areas
                                            }
                                            for alert in filtered_alerts
                                        ]
                                    }
                                    
                                    yield f"event: weather_alert\ndata: {json.dumps(alert_data)}\n\n"
                                    
                                    logger.info(f"Sent {len(filtered_alerts)} new alerts to connection {connection_id}")
                            
                            last_alert_check = current_time
                            
                        except Exception as e:
                            logger.warning(f"Could not check for new alerts: {e}")
                            last_alert_check = current_time
                    
                    # Send weather update every 2 minutes
                    if (current_time - last_weather_update).total_seconds() >= 120:
                        # Get current weather
                        weather = await self.weather_client.get_current_weather(location_key)
                        
                        # Prepare weather data with location info
                        weather_data = {
                            "type": "current_weather",
                            "location_key": location_key,
                            "zip_code": connection.zip_code,
                            "location_name": connection.location_name,
                            "timestamp": current_time.isoformat(),
                            "weather": {
                                "temperature": weather.temperature,
                                "temperature_unit": weather.temperature_unit,
                                "humidity": weather.humidity,
                                "wind_speed": weather.wind_speed,
                                "wind_direction": weather.wind_direction,
                                "pressure": weather.pressure,
                                "visibility": weather.visibility,
                                "uv_index": weather.uv_index,
                                "weather_text": weather.weather_text,
                                "weather_icon": weather.weather_icon,
                                "precipitation": weather.precipitation,
                                "local_time": weather.local_time.isoformat()
                            }
                        }
                        
                        yield f"event: weather_update\ndata: {json.dumps(weather_data)}\n\n"
                        
                        last_weather_update = current_time
                        logger.debug(f"Sent weather update to connection {connection_id}")
                    
                    # Wait 30 seconds before next heartbeat
                    await asyncio.sleep(30)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in weather stream for {connection_id}: {e}")
                    error_data = {
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    yield f"event: error\ndata: {json.dumps(error_data)}\n\n"
                    break
            
            logger.info(f"SSE stream ending for connection {connection_id}")
            self.remove_connection(connection_id)
        
        return event_generator()


class WeatherSSEApp:
    """FastAPI application for weather SSE endpoints"""
    
    def __init__(self, config: Config, weather_client: NationalWeatherServiceClient):
        self.config = config
        self.weather_client = weather_client
        self.sse_manager = WeatherSSEManager(config, weather_client)
        self.app = FastAPI(title="Clima MCP SSE Server", version="0.1.0")
        
        # Add CORS middleware for browser compatibility
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup FastAPI routes for SSE endpoints"""
        
        @self.app.on_event("startup")
        async def startup():
            # Ensure the weather client's HTTP client is properly initialized
            logger.info("Starting SSE manager and ensuring weather client is ready")
            await self.sse_manager.start()
        
        @self.app.on_event("shutdown")
        async def shutdown():
            # Properly close the weather client
            logger.info("Shutting down SSE manager and weather client")
            await self.sse_manager.stop()
            if hasattr(self.weather_client, '_client') and self.weather_client._client:
                await self.weather_client._client.aclose()
        
        @self.app.get("/weather/stream/{zip_code}")
        async def weather_stream(
            zip_code: str,
            request: Request,
            alert_types: str = "all"
        ):
            """SSE endpoint for weather updates using zip code"""
            try:
                # Generate unique connection ID
                connection_id = f"{request.client.host}_{int(time.time() * 1000)}"
                
                # Convert zip code to location key
                location_key, location_name = await self.sse_manager._zip_to_location_key(zip_code)
                
                # Parse alert types
                alert_type_set = set(alert_types.split(",")) if alert_types != "all" else {"all"}
                
                # Add connection with location info
                connection = self.sse_manager.add_connection(
                    connection_id=connection_id,
                    location_key=location_key,
                    zip_code=zip_code,
                    location_name=location_name,
                    alert_types=alert_type_set
                )
                
                # Create event generator
                event_generator = await self.sse_manager.get_current_weather_stream(location_key, connection_id)
                
                return StreamingResponse(event_generator, media_type="text/event-stream")
                
            except ValueError as e:
                logger.error(f"Invalid zip code {zip_code}: {e}")
                raise HTTPException(status_code=400, detail=f"Invalid zip code: {zip_code}")
            except Exception as e:
                logger.error(f"Error creating weather stream for zip {zip_code}: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/weather/status")
        async def status():
            """Get SSE server status"""
            return JSONResponse({
                "status": "running" if self.sse_manager.running else "stopped",
                "active_connections": len(self.sse_manager.connections),
                "monitored_locations": len(self.sse_manager.location_subscribers),
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.post("/weather/heartbeat/{connection_id}")
        async def heartbeat(connection_id: str):
            """Update connection heartbeat"""
            self.sse_manager.update_heartbeat(connection_id)
            return JSONResponse({"status": "ok", "timestamp": datetime.now().isoformat()})
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application"""
        return self.app 