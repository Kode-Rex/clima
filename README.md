# Clima MCP - AccuWeather API Wrapper

A comprehensive Model Context Protocol (MCP) server that wraps the AccuWeather API, providing weather data, forecasts, alerts, and real-time updates via Server-Sent Events (SSE).

## Features

- **FastMCP Integration**: Modern MCP server using FastMCP framework with clean decorator syntax
- **AccuWeather API Wrapper**: Complete integration with AccuWeather's weather services
- **Real-time Updates**: SSE support for live weather data streams
- **Weather Alerts**: Real-time weather alerts and warnings
- **Comprehensive Coverage**: Current weather, forecasts, historical data, and weather indices
- **Rate Limiting**: Built-in API rate limiting and caching
- **Error Handling**: Robust error handling and logging
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

3. **Get AccuWeather API Key**:
   - Sign up at [AccuWeather Developer Portal](https://developer.accuweather.com/)
   - Create an application and get your API key

4. **Configure environment**:
   ```bash
   cp env.example .env
   # Edit .env with your API key
   ```

## Configuration

The server uses environment variables for configuration. Create a `.env` file in the project root:

```bash
# Copy the example file and edit with your values
cp env.example .env
```

Configure your `.env` file with the following variables:

```bash
# AccuWeather API Configuration (Required)
ACCUWEATHER_API_KEY=your_api_key_here
ACCUWEATHER_BASE_URL=http://dataservice.accuweather.com

# Server Configuration
HOST=localhost
PORT=8000
DEBUG=false

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/clima-mcp.log

# SSE Configuration
SSE_HEARTBEAT_INTERVAL=30
SSE_MAX_CONNECTIONS=100

# Cache Configuration
CACHE_TTL_SECONDS=300
CACHE_MAX_SIZE=1000
```

**Note**: You can also set these as system environment variables instead of using a `.env` file. The `.env` file takes precedence over system environment variables.

## Usage

### MCP Server Mode

Run the server in MCP mode for AI assistant integration:

```bash
python main.py mcp
```

This starts the server in stdio mode, compatible with Claude Desktop and other MCP clients.

### SSE Server Mode

Run the server in HTTP mode with SSE endpoints:

```bash
python main.py sse
# Or with custom host/port
python main.py sse --host 0.0.0.0 --port 8080
```

### Test API Connection

Test your AccuWeather API setup:

```bash
python main.py test
```

## MCP Tools

The server provides the following MCP tools:

### Location Tools

- **`search_locations`**: Search for locations by name
  ```json
  {
    "query": "New York",
    "language": "en-us"
  }
  ```

- **`get_location_key`**: Get location key from coordinates
  ```json
  {
    "latitude": 40.7128,
    "longitude": -74.0060
  }
  ```

### Weather Data Tools

- **`get_current_weather`**: Get current weather conditions
  ```json
  {
    "location_key": "349727",
    "details": true
  }
  ```

- **`get_weather_forecast`**: Get 5-day weather forecast
  ```json
  {
    "location_key": "349727",
    "metric": true
  }
  ```

- **`get_hourly_forecast`**: Get hourly forecast
  ```json
  {
    "location_key": "349727",
    "hours": 12
  }
  ```

### Alert and Index Tools

- **`get_weather_alerts`**: Get active weather alerts
  ```json
  {
    "location_key": "349727"
  }
  ```

- **`get_weather_indices`**: Get weather indices (air quality, UV, etc.)
  ```json
  {
    "location_key": "349727",
    "index_id": 1
  }
  ```

- **`get_historical_weather`**: Get historical weather data
  ```json
  {
    "location_key": "349727",
    "start_date": "2024-01-01",
    "end_date": "2024-01-07"
  }
  ```

## SSE Endpoints

When running in SSE mode, the following endpoints are available:

### Weather Stream

Get real-time weather updates for a location:

```
GET /weather/stream/{location_key}?alert_types=all
```

**Parameters**:
- `location_key`: AccuWeather location key
- `alert_types`: Comma-separated alert types (`all`, `severe`, `tornado`, etc.)

**Example**:
```bash
curl -N http://localhost:8000/weather/stream/349727
```

### Server Status

Get SSE server status:

```
GET /weather/status
```

**Response**:
```json
{
  "status": "running",
  "active_connections": 5,
  "monitored_locations": 3,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Heartbeat

Update connection heartbeat:

```
POST /weather/heartbeat/{connection_id}
```

## SSE Event Types

The SSE stream sends the following event types:

### Weather Update Event

```json
{
  "type": "current_weather",
  "location_key": "349727",
  "timestamp": "2024-01-15T10:30:00Z",
  "weather": {
    "temperature": 15.0,
    "temperature_unit": "C",
    "humidity": 65,
    "wind_speed": 10.5,
    "wind_direction": "NW",
    "pressure": 1013.2,
    "visibility": 16.0,
    "uv_index": 3,
    "weather_text": "Partly Cloudy",
    "weather_icon": 3,
    "precipitation": 0.0,
    "local_time": "2024-01-15T10:30:00Z"
  }
}
```

### Weather Alert Event

```json
{
  "type": "weather_alert",
  "location_key": "349727",
  "timestamp": "2024-01-15T10:30:00Z",
  "alerts": [
    {
      "alert_id": "12345",
      "title": "Winter Storm Warning",
      "description": "Heavy snow expected...",
      "severity": "Severe",
      "category": "Winter",
      "start_time": "2024-01-15T12:00:00Z",
      "end_time": "2024-01-16T06:00:00Z",
      "areas": ["New York City", "Manhattan"]
    }
  ]
}
```

### Heartbeat Event

```json
{
  "type": "heartbeat",
  "timestamp": "2024-01-15T10:30:00Z",
  "active_connections": 5
}
```

## Integration with Claude Desktop

To use with Claude Desktop, add this configuration to your MCP settings:

```json
{
  "mcpServers": {
    "clima-mcp": {
      "command": "python",
      "args": ["/path/to/clima-mcp/main.py", "mcp"],
      "env": {
        "ACCUWEATHER_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## API Rate Limits

The server implements rate limiting to respect AccuWeather's API limits:

- **Free Tier**: 50 calls/day
- **Rate Limiting**: 1 second between requests
- **Caching**: 5-minute TTL for weather data
- **Connection Limits**: Max 100 SSE connections

## Error Handling

The server includes comprehensive error handling:

- **API Errors**: Graceful handling of AccuWeather API errors
- **Rate Limiting**: Automatic retry with backoff
- **Connection Management**: Automatic cleanup of expired SSE connections
- **Logging**: Detailed logging with configurable levels
- **Validation**: Input validation for all tools and endpoints

## Examples

### Python Client Example

```python
import asyncio
from weather_mcp.accuweather import AccuWeatherClient
from weather_mcp.config import get_config

async def get_weather():
    config = get_config()
    
    async with AccuWeatherClient(config) as client:
        # Search for a location
        locations = await client.search_locations("London")
        location_key = locations[0]["Key"]
        
        # Get current weather
        weather = await client.get_current_weather(location_key)
        print(f"Temperature: {weather.temperature}°{weather.temperature_unit}")
        print(f"Conditions: {weather.weather_text}")
        
        # Get forecast
        forecast = await client.get_5day_forecast(location_key)
        for day in forecast:
            print(f"{day.date}: {day.day_temperature}°")

asyncio.run(get_weather())
```

### JavaScript SSE Client Example

```javascript
const eventSource = new EventSource('http://localhost:8000/weather/stream/349727');

eventSource.onmessage = function(event) {
    const data = JSON.parse(event.data);
    
    if (data.type === 'current_weather') {
        console.log(`Temperature: ${data.weather.temperature}°${data.weather.temperature_unit}`);
        console.log(`Conditions: ${data.weather.weather_text}`);
    } else if (data.type === 'weather_alert') {
        console.log(`Weather Alert: ${data.alerts[0].title}`);
    }
};

eventSource.onerror = function(event) {
    console.error('SSE connection error:', event);
};
```

## Development

### Project Structure

```
clima-mcp/
├── weather_mcp/
│   ├── __init__.py          # Package initialization
│   ├── server.py            # MCP server implementation
│   ├── accuweather.py       # AccuWeather API client
│   ├── sse.py               # SSE implementation
│   └── config.py            # Configuration management
├── examples/
│   └── sse_client.html      # HTML demo for SSE testing
├── main.py                  # Main entry point
├── setup.py                 # Package setup
├── requirements.txt         # Python dependencies
├── env.example              # Environment configuration template
└── README.md               # This file
```

### Testing

```bash
# Test API connection
python main.py test

# Run with debug logging
LOG_LEVEL=DEBUG python main.py sse
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:

- Check the [AccuWeather API Documentation](https://developer.accuweather.com/)
- Review the [MCP Specification](https://modelcontextprotocol.io/)
- Open an issue in this repository

## Acknowledgments

- [AccuWeather](https://www.accuweather.com/) for weather data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the protocol specification
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [SSE-Starlette](https://github.com/sysid/sse-starlette) for SSE support
