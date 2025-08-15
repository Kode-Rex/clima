#!/usr/bin/env python3
"""
CLI entry point for Weather MCP Server
"""

import asyncio

import typer
from loguru import logger

from .config import Config, get_config, setup_logging
from .observability import observability

app = typer.Typer(
    name="clima-mcp",
    help="Weather API Server - National Weather Service Edition",
    add_completion=False,
)


def configure_logging(config: Config | None = None):
    """Configure logging for CLI"""
    if config is None:
        config = get_config()
    setup_logging(config)

    # Initialize observability
    if config.enable_tracing:
        observability.setup_tracing()
    if config.enable_metrics:
        observability.setup_metrics(config.metrics_port)


@app.command()
def test():
    """Test the National Weather Service API"""
    from .nws import NationalWeatherServiceClient
    from .services import WeatherTestingService

    async def run_test():
        configure_logging()
        logger.info("Testing National Weather Service API")

        async with NationalWeatherServiceClient() as client:
            testing_service = WeatherTestingService(client)
            await testing_service.test_nws_api()

    asyncio.run(run_test())


@app.command()
def run(
    host: str = typer.Option("0.0.0.0", help="Server host address"),
    port: int = typer.Option(8000, help="Server port"),
):
    """Run weather server with SSE endpoints and health checks"""
    import threading

    from fastmcp import FastMCP

    from .health import create_health_app
    from .nws import NationalWeatherServiceClient

    async def run_server():
        configure_logging()
        logger.info("Starting Weather API Server with SSE (National Weather Service)")

        # Create FastAPI app with CORS middleware
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(title="Weather MCP Server")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "OPTIONS"],
            allow_headers=["*"],
        )
        logger.info("Created FastAPI app with CORS middleware")

        # Initialize FastMCP server for weather only
        mcp_server: FastMCP = FastMCP("Weather API Server")

        # Initialize weather client
        weather_client = NationalWeatherServiceClient()

        # Setup weather tools for API access
        from .api_tools import setup_weather_tools

        setup_weather_tools(mcp_server, weather_client)

        # Add comprehensive weather SSE streaming endpoint
        import asyncio
        import json

        from fastapi.responses import StreamingResponse

        @app.get("/sse")
        async def weather_stream(zip_code: str = "10001"):
            """Stream comprehensive weather data via SSE"""

            async def generate_weather_stream():
                try:
                    # Send connection established message
                    yield f"data: {json.dumps({'type': 'connection', 'status': 'connected', 'message': 'Weather stream started'})}\n\n"

                    # Get all weather data for the location
                    logger.info(f"Fetching weather data for ZIP: {zip_code}")

                    # 1. Search for location
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Searching location...'})}\n\n"
                    locations = await weather_client.search_locations(zip_code)

                    if not locations:
                        yield f"data: {json.dumps({'type': 'error', 'message': f'No location found for ZIP: {zip_code}'})}\n\n"
                        return

                    location = locations[0]
                    location_key = location["Key"]
                    location_name = location["LocalizedName"]

                    yield f"data: {json.dumps({'type': 'location', 'data': {'name': location_name, 'key': location_key}})}\n\n"

                    # 2. Get current weather
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Fetching current weather...'})}\n\n"
                    weather = await weather_client.get_current_weather(location_key)

                    current_weather = {
                        "temperature": weather.temperature,
                        "temperature_unit": weather.temperature_unit,
                        "weather_text": weather.weather_text,
                        "humidity": weather.humidity,
                        "wind_speed": weather.wind_speed,
                        "wind_direction": weather.wind_direction,
                        "pressure": weather.pressure,
                        "visibility": weather.visibility,
                        "uv_index": weather.uv_index,
                        "precipitation": weather.precipitation,
                    }

                    yield f"data: {json.dumps({'type': 'current_weather', 'data': current_weather})}\n\n"

                    # 3. Get 5-day forecast
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Fetching 5-day forecast...'})}\n\n"
                    forecast = await weather_client.get_5day_forecast(location_key)

                    daily_forecasts = []
                    for day in forecast:
                        daily_forecasts.append(
                            {
                                "date": day.date.isoformat(),
                                "min_temperature": day.min_temperature,
                                "max_temperature": day.max_temperature,
                                "temperature_unit": day.temperature_unit,
                                "day_weather_text": day.day_weather_text,
                                "day_weather_icon": day.day_weather_icon,
                                "day_precipitation_probability": day.day_precipitation_probability,
                                "night_weather_text": day.night_weather_text,
                                "night_weather_icon": day.night_weather_icon,
                                "night_precipitation_probability": day.night_precipitation_probability,
                            }
                        )

                    yield f"data: {json.dumps({'type': 'forecast', 'data': daily_forecasts})}\n\n"

                    # 4. Get weather alerts
                    yield f"data: {json.dumps({'type': 'status', 'message': 'Checking weather alerts...'})}\n\n"
                    alerts = await weather_client.get_weather_alerts(location_key)

                    alert_list = []
                    for alert in alerts:
                        alert_list.append(
                            {
                                "alert_id": alert.alert_id,
                                "title": alert.title,
                                "description": alert.description,
                                "severity": alert.severity,
                                "category": alert.category,
                                "start_time": alert.start_time.isoformat(),
                                "end_time": alert.end_time.isoformat()
                                if alert.end_time
                                else None,
                                "areas": alert.areas,
                            }
                        )

                    yield f"data: {json.dumps({'type': 'alerts', 'data': alert_list, 'count': len(alert_list)})}\n\n"

                    # 5. Send completion message
                    yield f"data: {json.dumps({'type': 'complete', 'message': 'All weather data loaded', 'location': location_name})}\n\n"

                    # Keep connection alive with periodic updates
                    while True:
                        await asyncio.sleep(30)
                        yield f"data: {json.dumps({'type': 'heartbeat', 'timestamp': asyncio.get_event_loop().time()})}\n\n"

                except Exception as e:
                    logger.error(f"Error in weather stream: {e}")
                    yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

            return StreamingResponse(
                generate_weather_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                },
            )

        logger.info("Added comprehensive weather streaming endpoint")

        # Mount the MCP SSE app to the FastAPI app (deprecated but needed for SSE)
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            mcp_app = mcp_server.sse_app()
        app.mount("/", mcp_app)
        logger.info("Mounted FastMCP SSE server to FastAPI app")

        return app

    def run_health_server():
        """Run health check server on a separate port"""
        import uvicorn

        health_app = create_health_app()
        logger.info(f"Starting health server on port {port + 1}")
        uvicorn.run(health_app, host=host, port=port + 1, log_level="warning")

    # Start health server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()

    # Initialize the FastAPI app with mounted MCP server
    app = asyncio.run(run_server())

    # Run FastAPI app with FastMCP mounted (with CORS)
    logger.info(f"Weather MCP Server: http://{host}:{port}")
    logger.info(f"Health endpoints: http://{host}:{port + 1}/health")
    logger.info(f"Metrics endpoint: http://{host}:{port + 1}/metrics")
    logger.info(
        f"SSE Client: http://{host}:{port + 1}/client (CORS enabled via FastAPI)"
    )

    import uvicorn

    uvicorn.run(app, host=host, port=port)


@app.command()
def version():
    """Show version information"""
    from ._version import __version__

    typer.echo(f"Weather API Server v{__version__}")


def main():
    """Main CLI entry point"""
    app()


if __name__ == "__main__":
    main()
