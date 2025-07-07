# Weather MCP - National Weather Service Edition

A comprehensive Model Context Protocol (MCP) server that provides **completely free** weather data using the National Weather Service API. No API keys required!

## 🌟 Why This is Better

**Before (AccuWeather)**:
- ❌ API key required
- ❌ Rate limits on free tier
- ❌ Weather alerts cost $25/month
- ❌ Full alerts cost $250/month

**Now (National Weather Service)**:
- ✅ **Completely FREE** 
- ✅ **No API key needed**
- ✅ **Free weather alerts**
- ✅ **US Government data** (reliable!)
- ✅ **No rate limits**

## Features

- **FastMCP Integration**: Modern MCP server using FastMCP framework
- **National Weather Service API**: Free, reliable US government weather data
- **Real-time Updates**: SSE support for live weather data streams
- **Weather Alerts**: Free real-time weather alerts and warnings
- **Comprehensive Coverage**: Current weather, forecasts, and alerts
- **Zero Configuration**: No API keys or registration required
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

The server provides 8 weather tools:

### Location Tools

- **`search_locations`**: Search for locations by name or ZIP code
- **`get_location_weather`**: Get weather by searching for a location first

### Weather Data Tools

- **`get_current_weather`**: Get current weather conditions
- **`get_5day_forecast`**: Get 5-day weather forecast
- **`get_location_forecast`**: Get forecast by searching for a location first

### Alert Tools

- **`get_weather_alerts`**: Get active weather alerts (FREE!)
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
- Free weather alerts
- Heartbeat every 30 seconds
- Zip code to coordinates conversion

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

The National Weather Service covers:
- 🇺🇸 **United States** (all states and territories)
- **ZIP codes** supported for easy location lookup
- **Coordinates** for precise location targeting

## Comparison with AccuWeather

| Feature | AccuWeather | National Weather Service |
|---------|-------------|--------------------------|
| API Key | Required | ❌ **None needed** |
| Cost | Free tier limited | ✅ **Completely free** |
| Weather Alerts | $25-250/month | ✅ **Free** |
| Rate Limits | Yes | ✅ **None** |
| Coverage | Global | US (comprehensive) |
| Data Source | Commercial | ✅ **US Government** |
| Reliability | Good | ✅ **Excellent** |

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

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python run_tests.py`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Migration from AccuWeather

If you were using the AccuWeather version:

1. **Remove** your `.env` file (no API keys needed!)
2. **Update** location keys (now use lat,lon format)
3. **Test** with `python main.py test`
4. **Enjoy** free weather alerts! 🎉
