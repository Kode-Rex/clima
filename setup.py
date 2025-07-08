#!/usr/bin/env python3
"""
Setup script for Clima MCP
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="clima-mcp",
    version="0.1.0",
    author="Climate MCP Team",
    author_email="",
    description="National Weather Service API wrapper with MCP server and SSE support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/clima-mcp",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "clima-mcp=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "weather_mcp": ["*.py"],
        "examples": ["*.html", "*.py", "*.js"],
    },
    keywords="weather, mcp, nws, national-weather-service, api, sse, server-sent-events, climate",
    project_urls={
        "Bug Reports": "https://github.com/your-org/clima-mcp/issues",
        "Source": "https://github.com/your-org/clima-mcp",
        "Documentation": "https://github.com/your-org/clima-mcp#readme",
    },
) 