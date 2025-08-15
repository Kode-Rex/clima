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
    help="Weather MCP Server - National Weather Service Edition",
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
def mcp():
    """Run MCP server mode"""
    from fastmcp import FastMCP

    from .mcp_tools import setup_mcp_tools
    from .nws import NationalWeatherServiceClient

    async def run_mcp():
        configure_logging()
        logger.info("Starting Weather MCP Server (National Weather Service)")

        # Initialize FastMCP
        mcp_server: FastMCP = FastMCP("Weather MCP")

        # Initialize weather client
        weather_client = NationalWeatherServiceClient()

        # Setup MCP tools
        setup_mcp_tools(mcp_server, weather_client)

        return mcp_server

    # Initialize dependencies
    mcp_server = asyncio.run(run_mcp())

    # Run MCP server with its own event loop
    mcp_server.run(transport="stdio")


@app.command()
def sse(
    host: str = typer.Option("0.0.0.0", help="Server host address"),
    port: int = typer.Option(8000, help="Server port"),
):
    """Run SSE server mode"""
    import uvicorn

    from .nws import NationalWeatherServiceClient
    from .sse import WeatherSSEApp

    async def run_sse():
        configure_logging()
        logger.info("Starting Weather MCP SSE Server (National Weather Service)")

        config = Config(host=host, port=port)

        async with NationalWeatherServiceClient() as client:
            sse_app = WeatherSSEApp(config, client)
            app = sse_app.get_app()

            # Use uvicorn server directly
            server_config = uvicorn.Config(app, host=config.host, port=config.port)
            server = uvicorn.Server(server_config)
            await server.serve()

    asyncio.run(run_sse())


@app.command()
def version():
    """Show version information"""
    from ._version import __version__

    typer.echo(f"Weather MCP Server v{__version__}")


def main():
    """Main CLI entry point"""
    app()


if __name__ == "__main__":
    main()
