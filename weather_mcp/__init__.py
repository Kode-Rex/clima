"""
Clima MCP - AccuWeather API wrapper with MCP server and SSE support
"""

__version__ = "0.1.0"
__author__ = "Climate MCP Team"

from .server import create_server, mcp
from .config import Config

__all__ = ["create_server", "mcp", "Config"] 