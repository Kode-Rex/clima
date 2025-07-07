# Weather MCP - National Weather Service Edition

A comprehensive Model Context Protocol (MCP) server that provides **completely free** weather data using the National Weather Service API. Built with FastMCP for modern AI assistant integration.

## Features

- **Zero Cost**: Completely free weather data from the US Government
- **No API Keys**: No registration or authentication required
- **FastMCP Integration**: Modern MCP server using FastMCP framework
- **National Weather Service API**: Reliable, official US government weather data
- **Real-time Updates**: SSE support for live weather data streams
- **Weather Alerts**: Free real-time weather alerts and warnings
- **Comprehensive Coverage**: Current weather, forecasts, and alerts
- **Multiple Modes**: Run as MCP server or standalone SSE server

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd clima-mcp
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **That's it!** No API keys needed - the National Weather Service API is completely free.

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
main.py (FastMCP server)
├── weather_mcp/
│   ├── nws.py (National Weather Service client)
│   ├── sse.py (Server-Sent Events)
│   └── config.py (Configuration)
├── examples/
│   └── sse_client.html (Live demo)
└── tests/ (Complete test suite)
```

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

## Testing

Run the comprehensive test suite:

```bash
python run_tests.py
```

**Test Coverage**:
- Unit tests for all weather tools
- Integration tests for SSE server
- Configuration validation tests
- Mock API responses for CI/CD

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python run_tests.py`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
- Review the [National Weather Service API documentation](https://www.weather.gov/documentation/services-web-api)
- Check the [Model Context Protocol specification](https://modelcontextprotocol.io/)
- Open an issue in this repository

## Acknowledgments

- [National Weather Service](https://www.weather.gov/) for providing free, reliable weather data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the protocol specification
- [FastMCP](https://github.com/jlowin/fastmcp) for the modern MCP framework
- [OpenStreetMap](https://www.openstreetmap.org/) for geocoding services
