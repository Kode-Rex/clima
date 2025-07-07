#!/usr/bin/env python3
"""
Main entry point for Clima MCP Server
"""

import asyncio
import argparse
import sys
from pathlib import Path

import uvicorn
from loguru import logger

from weather_mcp.config import get_config, setup_logging
from weather_mcp.server import create_server, mcp
from weather_mcp.accuweather import AccuWeatherClient  
from weather_mcp.sse import WeatherSSEApp


async def run_mcp_server():
    """Run the MCP server in stdio mode"""
    try:
        config = get_config()
        setup_logging(config)
        
        logger.info("Starting FastMCP Clima Server in stdio mode")
        server = create_server(config)
        await server.run()
        
    except KeyboardInterrupt:
        logger.info("MCP Server stopped by user")
    except Exception as e:
        logger.error(f"MCP Server error: {e}")
        sys.exit(1)


def run_sse_server(host: str = None, port: int = None):
    """Run the SSE server with FastAPI/Uvicorn"""
    try:
        config = get_config()
        setup_logging(config)
        
        # Use provided host/port or config defaults
        server_host = host or config.host
        server_port = port or config.port
        
        logger.info(f"Starting Clima SSE Server on {server_host}:{server_port}")
        
        # Create weather client and SSE app
        weather_client = AccuWeatherClient(config)
        sse_app = WeatherSSEApp(config, weather_client)
        
        # Run uvicorn server
        uvicorn.run(
            sse_app.get_app(),
            host=server_host,
            port=server_port,
            log_level=config.log_level.lower(),
            access_log=config.debug
        )
        
    except KeyboardInterrupt:
        logger.info("SSE Server stopped by user")
    except Exception as e:
        logger.error(f"SSE Server error: {e}")
        sys.exit(1)


async def test_accuweather_api():
    """Test AccuWeather API connection"""
    try:
        config = get_config()
        setup_logging(config)
        
        logger.info("Testing AccuWeather API connection...")
        
        async with AccuWeatherClient(config) as client:
            # Test location search
            locations = await client.search_locations("New York")
            if locations:
                location = locations[0]
                location_key = location["Key"]
                location_name = location["LocalizedName"]
                
                logger.info(f"Found location: {location_name} (Key: {location_key})")
                
                # Test current weather
                weather = await client.get_current_weather(location_key)
                logger.info(f"Current weather: {weather.temperature}°{weather.temperature_unit}, {weather.weather_text}")
                
                # Test forecast
                forecast = await client.get_5day_forecast(location_key)
                logger.info(f"5-day forecast: {len(forecast)} days")
                
                # Test alerts
                alerts = await client.get_weather_alerts(location_key)
                logger.info(f"Weather alerts: {len(alerts)} active")
                
                logger.info("✅ AccuWeather API test successful!")
            else:
                logger.error("❌ No locations found for 'New York'")
                
    except Exception as e:
        logger.error(f"❌ AccuWeather API test failed: {e}")
        sys.exit(1)


def main():
    """Main entry point with command line argument parsing"""
    parser = argparse.ArgumentParser(description="Clima MCP Server - AccuWeather API wrapper")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # MCP server command
    mcp_parser = subparsers.add_parser("mcp", help="Run MCP server (stdio mode)")
    
    # SSE server command
    sse_parser = subparsers.add_parser("sse", help="Run SSE server (HTTP mode)")
    sse_parser.add_argument("--host", default=None, help="Server host (default: from config)")
    sse_parser.add_argument("--port", type=int, default=None, help="Server port (default: from config)")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test AccuWeather API connection")
    
    # Help command
    help_parser = subparsers.add_parser("help", help="Show help information")
    
    args = parser.parse_args()
    
    if args.command == "mcp":
        asyncio.run(run_mcp_server())
    
    elif args.command == "sse":
        run_sse_server(host=args.host, port=args.port)
    
    elif args.command == "test":
        asyncio.run(test_accuweather_api())
    
    elif args.command == "help" or not args.command:
        parser.print_help()
        print("\nExamples:")
        print("  python main.py mcp              # Run MCP server")
        print("  python main.py sse              # Run SSE server")
        print("  python main.py sse --port 8080  # Run SSE server on port 8080")
        print("  python main.py test             # Test API connection")
        print("\nEnvironment Configuration:")
        print("  Copy env.example to .env and configure:")
        print("  ACCUWEATHER_API_KEY=<your_api_key>")
        print("  ACCUWEATHER_BASE_URL=http://dataservice.accuweather.com")
        print("  See env.example for all available options.")
    
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main() 