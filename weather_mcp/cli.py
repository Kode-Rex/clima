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
