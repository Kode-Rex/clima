#!/usr/bin/env python3
"""
CLI entry point for Weather MCP Server
"""

import asyncio

import typer
from loguru import logger

from .config import Config, setup_logging

app = typer.Typer(
    name="clima-mcp",
    help="Weather API Server - National Weather Service Edition",
    add_completion=False,
)


def configure_logging(config: Config | None = None):
    """Configure logging for CLI"""
    if config is None:
        config = Config()
    setup_logging(config)


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
    """Run weather server with SSE endpoints"""
    from fastmcp import FastMCP

    from .nws import NationalWeatherServiceClient

    async def run_server():
        configure_logging()
        logger.info("Starting Weather API Server with SSE (National Weather Service)")

        # Initialize FastMCP with SSE support
        mcp_server: FastMCP = FastMCP("Weather API Server")

        # Initialize weather client
        weather_client = NationalWeatherServiceClient()

        # Setup weather tools for API access
        from .api_tools import setup_weather_tools

        setup_weather_tools(mcp_server, weather_client)

        return mcp_server

    # Initialize and run server
    mcp_server = asyncio.run(run_server())

    # Run FastMCP server with SSE transport
    mcp_server.run(transport="sse", host=host, port=port)


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
