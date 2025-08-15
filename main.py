#!/usr/bin/env python3
"""
Weather MCP Server - National Weather Service Edition
Provides weather data and alerts using free NWS API
"""

import asyncio
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from loguru import logger

from weather_mcp.config import Config
from weather_mcp.mcp_tools import setup_mcp_tools
from weather_mcp.nws import NationalWeatherServiceClient
from weather_mcp.services import WeatherTestingService
from weather_mcp.sse import WeatherSSEApp

# Configure logging
logger.remove()
logger.add(
    sys.stderr,
    format="{time} | {level} | {name}:{function}:{line} - {message}",
    level="INFO",
)

# Initialize FastMCP
mcp = FastMCP("Weather MCP")

# Global weather client
weather_client: NationalWeatherServiceClient | None = None


@asynccontextmanager
async def get_weather_client():
    """Get weather client context manager"""
    global weather_client
    try:
        weather_client = NationalWeatherServiceClient()
        yield weather_client
    finally:
        if weather_client:
            await weather_client.close()


async def run_test_mode():
    """Run API test mode"""
    async with get_weather_client() as client:
        testing_service = WeatherTestingService(client)
        await testing_service.test_nws_api()


async def run_sse_mode():
    """Run SSE server mode"""
    logger.info("Starting Weather MCP SSE Server (National Weather Service)")

    config = Config()
    async with get_weather_client() as client:
        sse_app = WeatherSSEApp(config, client)
        app = sse_app.get_app()

        # Use uvicorn server directly to avoid asyncio.run() conflict
        import uvicorn

        server_config = uvicorn.Config(app, host="0.0.0.0", port=8000)
        server = uvicorn.Server(server_config)
        await server.serve()


async def run_mcp_mode():
    """Run MCP server mode"""
    logger.info("Starting Weather MCP Server (National Weather Service)")

    global weather_client
    weather_client = NationalWeatherServiceClient()

    # Setup MCP tools
    setup_mcp_tools(mcp, weather_client)


async def main():
    """Main application entry point"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == "test":
            await run_test_mode()
        elif mode == "sse":
            await run_sse_mode()
        elif mode == "mcp":
            await run_mcp_mode()
        else:
            logger.error(f"Unknown mode: {mode}")
            logger.info("Usage: python main.py [test|sse|mcp]")
            sys.exit(1)
    else:
        # Default to MCP mode
        await run_mcp_mode()


if __name__ == "__main__":
    # Handle different modes with appropriate event loop management
    if len(sys.argv) > 1 and sys.argv[1] in ["test", "sse"]:
        # For test and sse modes, use normal asyncio.run()
        asyncio.run(main())
    else:
        # For MCP mode, let FastMCP handle the event loop entirely
        asyncio.run(main())  # Initialize dependencies

        # Now run MCP server with its own event loop
        mcp.run(transport="stdio")
