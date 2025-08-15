#!/usr/bin/env python3
"""
Weather MCP Server - National Weather Service Edition
Provides weather data and alerts using free NWS API

This is a fallback entry point. Use 'clima-mcp' command for the modern CLI.
"""

import warnings


def main():
    """Fallback main entry point - redirects to modern CLI"""
    warnings.warn(
        "Direct execution of main.py is deprecated. Use 'clima-mcp' command instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # Import and use the modern CLI
    from weather_mcp.cli import main as cli_main

    cli_main()


if __name__ == "__main__":
    main()
