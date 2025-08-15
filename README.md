# Weather MCP - National Weather Service Edition

A comprehensive Model Context Protocol (MCP) server that provides **completely free** weather data using the National Weather Service API. Built with FastMCP for modern AI assistant integration.

## Features

### Core Weather Features
- **Zero Cost**: Completely free weather data from the US Government
- **No API Keys**: No registration or authentication required
- **FastMCP Integration**: Modern MCP server using FastMCP framework
- **National Weather Service API**: Reliable, official US government weather data
- **Real-time Updates**: SSE support for live weather data streams
- **Weather Alerts**: Free real-time weather alerts and warnings
- **Comprehensive Coverage**: Current weather, forecasts, and alerts
- **Multiple Modes**: Run as MCP server or standalone SSE server

### Development Features
- **Modern Python**: Built with Python 3.11+ and modern tooling
- **Type Safety**: Full type hints with MyPy validation
- **Code Quality**: Automated formatting (Black) and linting (Ruff)
- **Comprehensive Testing**: 71+ tests with pytest and async support
- **Docker Support**: Container-ready with docker-compose
- **CI/CD Pipeline**: GitHub Actions for automated testing and quality checks
- **Developer Experience**: Makefile with convenient development commands
- **Modular Architecture**: Clean service layer with individual test files

## Installation

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd clima-mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Set up development environment** (optional):
   ```bash
   make dev-setup
   ```

4. **That's it!** No API keys needed - the National Weather Service API is completely free.

### Alternative Installation Methods

#### Using pip only:
```bash
pip install -r requirements.txt
```

#### Using Docker:
```bash
docker-compose up --build
```

#### Using Makefile (recommended for development):
```bash
make install-dev
make dev-setup
```

## Usage

### Test the API (Recommended First Step)

```bash
python main.py test
```

You should see:
```
✓ Location search successful: 10001, Manhattan
✓ Current weather: 81.0°F, Clear
✓ 5-day forecast: 5 days retrieved
✓ Weather alerts: 1 active alerts
🎉 All NWS API tests passed!
```

### MCP Server Mode

Run the server in MCP mode for AI assistant integration:

```bash
python main.py mcp
```

### SSE Server Mode

Run the server in HTTP mode with real-time weather streams:

```bash
python main.py sse
```

Then visit: http://localhost:8000/examples/sse_client.html

## MCP Tools

The server provides 8 comprehensive weather tools:

### Location Tools

- **`search_locations`**: Search for locations by name or ZIP code
- **`get_location_weather`**: Get weather by searching for a location first

### Weather Data Tools

- **`get_current_weather`**: Get current weather conditions
- **`get_5day_forecast`**: Get 5-day weather forecast
- **`get_location_forecast`**: Get forecast by searching for a location first

### Alert Tools

- **`get_weather_alerts`**: Get active weather alerts (completely free!)
- **`get_location_alerts`**: Get alerts by searching for a location first

## SSE Endpoints

Real-time weather streaming endpoints:

### Weather Stream with Zip Codes

```
GET /weather/stream/{zip_code}?alert_types=all
```

**Example**:
```bash
# Stream weather for New York City
curl -N http://localhost:8000/weather/stream/10001

# Stream with specific alert types
curl -N http://localhost:8000/weather/stream/90210?alert_types=severe,tornado
```

**Features**:
- Real-time weather updates every 2 minutes
- Immediate weather data on connection
- Free weather alerts from National Weather Service
- Heartbeat every 30 seconds
- Automatic zip code to coordinates conversion

### Server Status

```
GET /weather/status
```

Returns server health and connection count.

## Example Usage

### Python MCP Client

```python
from weather_mcp import NationalWeatherServiceClient

async with NationalWeatherServiceClient() as client:
    # Search by zip code
    locations = await client.search_locations("10001")
    location_key = locations[0]["Key"]

    # Get current weather
    weather = await client.get_current_weather(location_key)
    print(f"Temperature: {weather.temperature}°{weather.temperature_unit}")

    # Get alerts (completely free!)
    alerts = await client.get_weather_alerts(location_key)
    print(f"Active alerts: {len(alerts)}")
```

### JavaScript SSE Client

```javascript
const eventSource = new EventSource('http://localhost:8000/weather/stream/10001');

eventSource.addEventListener('weather_update', function(event) {
    const data = JSON.parse(event.data);
    console.log(`Temperature: ${data.weather.temperature}°F`);
});

eventSource.addEventListener('weather_alert', function(event) {
    const data = JSON.parse(event.data);
    console.log(`Weather Alert: ${data.alerts[0].title}`);
});
```

## Coverage Area

The National Weather Service provides comprehensive coverage for:
- 🇺🇸 **United States** (all 50 states and territories)
- **ZIP codes** supported for easy location lookup
- **Coordinates** for precise location targeting
- **Puerto Rico, US Virgin Islands, Guam** and other US territories

## Architecture

```
main.py (FastMCP server entry point)
├── weather_mcp/
│   ├── nws.py (National Weather Service client)
│   ├── sse.py (Server-Sent Events)
│   ├── config.py (Configuration management)
│   ├── models.py (Pydantic data models)
│   ├── mcp_tools.py (MCP tool handlers)
│   ├── exceptions.py (Custom exceptions)
│   └── services/ (Service layer architecture)
│       ├── location_service.py
│       ├── weather_service.py
│       ├── forecast_service.py
│       ├── alert_service.py
│       ├── raw_weather_service.py
│       └── testing_service.py
├── tests/ (Comprehensive test suite)
│   ├── test_location_service.py
│   ├── test_weather_service.py
│   ├── test_forecast_service.py
│   ├── test_alert_service.py
│   ├── test_raw_weather_service.py
│   ├── test_testing_service.py
│   ├── test_weather_config.py
│   └── test_weather_server.py
├── examples/
│   └── sse_client.html (Live demo)
├── .github/workflows/ (CI/CD pipelines)
├── Dockerfile & docker-compose.yml
├── pyproject.toml (Modern Python project config)
├── Makefile (Development commands)
└── .pre-commit-config.yaml (Code quality automation)
```

### Service Layer Architecture

The application follows a clean service-oriented architecture:

- **Services**: Business logic for weather operations
- **Models**: Pydantic data validation and serialization
- **MCP Tools**: Protocol handlers that delegate to services
- **Configuration**: Environment-based settings management
- **Exception Handling**: Custom exceptions for better error management

### Modern Python Project Structure

The project uses modern Python packaging and tooling:

- **pyproject.toml**: Modern Python project configuration
- **Ruff**: Fast linting and code formatting
- **MyPy**: Static type checking
- **Pre-commit**: Automated quality checks
- **GitHub Actions**: CI/CD with testing and security scanning
- **Docker**: Containerized deployment options

## Technical Details

### Data Sources

- **Current Weather**: NWS observation stations
- **Forecasts**: NWS gridded forecast data
- **Alerts**: NWS weather alerts and warnings
- **Location Data**: OpenStreetMap Nominatim geocoding

### Performance

- **No Rate Limits**: Government API with no request restrictions
- **Caching**: Built-in caching for optimal performance
- **Async**: Full async/await support for concurrent requests
- **Real-time**: SSE streaming for live updates

### Reliability

- **Government Source**: Official US National Weather Service data
- **High Availability**: Government-maintained infrastructure
- **No API Keys**: No authentication failures or key expiration
- **Comprehensive Error Handling**: Graceful degradation on failures

## Configuration

The server can be configured through environment variables or a `.env` file:

```bash
# Server Configuration
HOST=localhost
PORT=8000
DEBUG=false
LOG_LEVEL=INFO

# SSE Configuration
SSE_HEARTBEAT_INTERVAL=30
SSE_MAX_CONNECTIONS=100
SSE_CONNECTION_TIMEOUT=300

# Cache Configuration
CACHE_TTL_SECONDS=300
CACHE_MAX_SIZE=1000
```

## Development & Testing

### Quick Development Commands

The project includes a comprehensive `Makefile` for easy development:

```bash
# Development setup
make dev-setup          # Full development environment setup
make install-dev         # Install with development dependencies

# Code quality
make format             # Format code with Black and Ruff
make lint               # Run linting checks
make type-check         # Run MyPy type checking
make pre-commit         # Run pre-commit hooks

# Testing
make test              # Run all tests
make test-unit         # Run unit tests only
make test-integration  # Run integration tests only
make coverage          # Run tests with coverage report

# Application
make run-test          # Test the NWS API
make run-mcp           # Run MCP server
make run-sse           # Run SSE server

# Cleanup
make clean             # Clean build artifacts
```

### Traditional Testing

Run the comprehensive test suite:

```bash
python run_tests.py
```

With options:
```bash
python run_tests.py --type unit --coverage --verbose
python run_tests.py --type integration --fail-fast
python run_tests.py --parallel 4
```

**Test Coverage**:
- Unit tests for all weather services (individual service test files)
- Integration tests for MCP and SSE servers
- Configuration validation tests
- Mock API responses for CI/CD
- 71 comprehensive tests with modular structure

### Code Quality Tools

The project uses modern Python development tools:

- **Black**: Code formatting
- **Ruff**: Fast linting and import sorting
- **MyPy**: Static type checking
- **Pre-commit hooks**: Automated quality checks
- **Pytest**: Testing framework with async support
- **GitHub Actions**: Automated CI/CD pipeline

### Development Workflow

1. **Set up environment**:
   ```bash
   make dev-setup
   ```

2. **Make changes and test**:
   ```bash
   make format
   make lint
   make test
   ```

3. **Commit changes** (pre-commit hooks run automatically):
   ```bash
   git add .
   git commit -m "Your changes"
   ```

### Docker Development

Run with Docker for consistent environment:

```bash
# Production mode
docker-compose up

# Development mode with hot reload
docker-compose --profile dev up
```

## Contributing

We welcome contributions! The project includes comprehensive development tools to make contributing easy.

### Development Setup

1. **Fork and clone the repository**
2. **Set up development environment**:
   ```bash
   make dev-setup
   ```
3. **Make your changes**
4. **Run quality checks**:
   ```bash
   make format        # Format code
   make lint          # Check linting
   make type-check    # Type checking
   make test          # Run tests
   ```
5. **Commit and push** (pre-commit hooks ensure quality)
6. **Submit a pull request**

### Code Quality Standards

- **Type hints** required for all functions
- **Docstrings** for all public methods
- **Tests** for new functionality
- **Code formatting** with Black
- **Linting** compliance with Ruff
- **100% test coverage** for new features

### Continuous Integration

The project uses GitHub Actions for:
- **Automated testing** on Python 3.11 and 3.12
- **Code quality checks** (formatting, linting, type checking)
- **Security scanning** with Bandit
- **Coverage reporting** to Codecov
- **Docker builds** validation

### Project Structure

- Follow the existing service layer architecture
- Add tests for each new service in corresponding test files
- Update documentation for new features
- Use the custom exception classes for error handling

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Review the [National Weather Service API documentation](https://www.weather.gov/documentation/services-web-api)
- Check the [Model Context Protocol specification](https://modelcontextprotocol.io/)
- Open an issue in this repository

## Badges

![Tests](https://github.com/your-org/clima-mcp/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![Code style](https://img.shields.io/badge/code%20style-black-000000.svg)
![Type checked](https://img.shields.io/badge/mypy-checked-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## Acknowledgments

- [National Weather Service](https://www.weather.gov/) for providing free, reliable weather data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the protocol specification
- [FastMCP](https://github.com/jlowin/fastmcp) for the modern MCP framework
- [OpenStreetMap](https://www.openstreetmap.org/) for geocoding services
- Python community for excellent development tools (Black, Ruff, MyPy, Pytest)
