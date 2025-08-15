# Weather MCP Observability Guide

This guide covers the comprehensive observability features added to the Weather MCP server, including metrics, logging, tracing, and monitoring dashboards.

## 🔍 Overview

The Weather MCP server now includes a complete observability stack with:

- **Prometheus** - Metrics collection and alerting
- **Grafana** - Visualization and dashboards
- **Loki** - Log aggregation and analysis
- **AlertManager** - Alert routing and notifications
- **Structured Logging** - JSON-formatted logs with correlation IDs
- **Distributed Tracing** - Request flow tracking
- **Health Endpoints** - Service health monitoring

## 🚀 Quick Start

### 1. Start the Full Observability Stack

```bash
# Option 1: Use the convenience script
make start-observability

# Option 2: Start manually
make observability-up
```

### 2. Access Monitoring Tools

- **Weather MCP API**: http://localhost:8000
- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9091
- **AlertManager**: http://localhost:9093
- **Health Check**: http://localhost:8000/health
- **Metrics Endpoint**: http://localhost:8000/metrics

### 3. Quick Health Check

```bash
# Check all services
make observability-status

# Check specific endpoints
make health-check
make metrics-check
```

## 📊 Metrics Collection

### API Metrics

The following metrics are automatically collected:

#### Request Metrics
- `weather_api_requests_total` - Total API requests by endpoint and status
- `weather_api_request_duration_seconds` - Request latency histograms
- `weather_errors_total` - Error counts by service and type

#### External API Metrics
- `nws_api_requests_total` - National Weather Service API requests
- `nws_api_request_duration_seconds` - NWS API response times

#### Cache Metrics
- `cache_operations_total` - Cache operations (hit/miss/set/error)

#### SSE Metrics
- `sse_connections_active` - Current active SSE connections
- `sse_connections_total` - Total SSE connections by status

#### Data Quality Metrics
- `weather_data_freshness_seconds` - Age of weather data by location

### Custom Metrics

You can add custom metrics using the observability decorators:

```python
from weather_mcp.observability import track_api_request, track_nws_request

@track_api_request("my_endpoint", "GET")
async def my_api_function():
    # Your API logic here
    pass

@track_nws_request("weather")
async def call_nws_api():
    # NWS API call logic
    pass
```

## 📝 Structured Logging

### Log Format

Logs are output in structured JSON format with the following fields:

```json
{
  "time": "2024-01-15 10:30:45.123",
  "level": "INFO",
  "name": "weather_mcp.services.weather_service",
  "function": "get_current_weather",
  "line": 25,
  "message": "API request completed",
  "extra": {
    "correlation_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "endpoint": "current_weather",
    "method": "GET",
    "status_code": "200",
    "duration": 0.234,
    "success": true
  }
}
```

### Correlation IDs

Every request gets a unique correlation ID that tracks the request through all services and logs, making debugging much easier.

### Log Levels

- `DEBUG` - Detailed debugging information
- `INFO` - General operational information
- `WARNING` - Warning conditions
- `ERROR` - Error conditions
- `CRITICAL` - Critical error conditions

## 🏥 Health Endpoints

### Available Endpoints

#### `/health`
General health check with basic metrics:
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": 1642234567.123,
  "metrics": {
    "active_sse_connections": 5,
    "total_api_requests": 1234,
    "total_nws_requests": 567,
    "total_errors": 2
  }
}
```

#### `/health/ready`
Readiness check for Kubernetes deployments:
```bash
curl http://localhost:8000/health/ready
```

#### `/health/live`
Liveness check for Kubernetes deployments:
```bash
curl http://localhost:8000/health/live
```

#### `/metrics`
Prometheus metrics endpoint:
```bash
curl http://localhost:8000/metrics
```

## 📈 Grafana Dashboards

### Weather MCP Service Dashboard

The included dashboard provides:

#### Service Overview
- API request rate
- 95th percentile latency
- Error rate
- Active SSE connections

#### API Performance
- Request rate by endpoint
- Response time percentiles (50th, 95th, 99th)
- Status code distribution

#### External Dependencies
- NWS API request rate and latency
- Dependency health status

#### Cache & SSE Performance
- Cache hit rate
- SSE connection patterns
- Connection lifecycle metrics

### Accessing Dashboards

1. Open Grafana: http://localhost:3000
2. Login with `admin` / `admin`
3. Navigate to the "Weather MCP Service Dashboard"

## 🚨 Alerting

### Pre-configured Alerts

The system includes the following alert rules:

#### Critical Alerts
- **Service Down** - Weather MCP service is unreachable
- **NWS API Failures** - High failure rate from National Weather Service

#### Warning Alerts
- **High Error Rate** - Overall error rate > 10%
- **High API Latency** - 95th percentile > 2 seconds
- **Low Cache Hit Rate** - Cache hit rate < 70%
- **Too Many SSE Connections** - Active connections > 80
- **Stale Weather Data** - Data older than 1 hour

### Alert Configuration

Alerts are configured in `monitoring/prometheus/alert_rules.yml` and routed through AlertManager (`monitoring/alertmanager/alertmanager.yml`).

To configure Slack notifications:
1. Edit `monitoring/alertmanager/alertmanager.yml`
2. Uncomment the Slack configuration section
3. Add your Slack webhook URL
4. Restart AlertManager: `make observability-restart`

## 🐳 Docker Configuration

### Services Included

The observability stack includes:

- **clima-mcp** - Main Weather MCP service with metrics enabled
- **prometheus** - Metrics collection (port 9091)
- **grafana** - Dashboards and visualization (port 3000)
- **loki** - Log aggregation (port 3100)
- **promtail** - Log shipping agent
- **alertmanager** - Alert routing (port 9093)
- **node-exporter** - System metrics (port 9100)
- **cadvisor** - Container metrics (port 8080)

### Development Mode

For development with hot reload:

```bash
# Start development stack
docker-compose -f docker-compose.observability.yml --profile dev up

# Or using Makefile
make observability-up
```

## ⚙️ Configuration

### Environment Variables

Observability features can be configured via environment variables:

```bash
# Enable/disable features
ENABLE_METRICS=true
ENABLE_TRACING=true
STRUCTURED_LOGGING=true

# Ports
METRICS_PORT=9090

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/clima-mcp.log
```

### Custom Configuration

Edit these files to customize the observability stack:

- `monitoring/prometheus/prometheus.yml` - Prometheus configuration
- `monitoring/grafana/provisioning/` - Grafana datasources and dashboards
- `monitoring/loki/loki.yml` - Loki log aggregation settings
- `monitoring/alertmanager/alertmanager.yml` - Alert routing rules

## 🔧 Troubleshooting

### Common Issues

#### Services Not Starting
```bash
# Check Docker logs
make observability-logs

# Check individual service logs
docker-compose -f docker-compose.observability.yml logs prometheus
docker-compose -f docker-compose.observability.yml logs grafana
```

#### Metrics Not Appearing
1. Verify metrics endpoint: `curl http://localhost:8000/metrics`
2. Check Prometheus targets: http://localhost:9091/targets
3. Verify Prometheus can scrape the service

#### Grafana Dashboard Empty
1. Check Prometheus datasource connection in Grafana
2. Verify metrics are being collected: http://localhost:9091/graph
3. Check dashboard queries match your metric names

#### Logs Not Appearing in Loki
1. Check Promtail configuration: `monitoring/promtail/promtail.yml`
2. Verify log file permissions and paths
3. Check Promtail logs: `docker-compose -f docker-compose.observability.yml logs promtail`

### Performance Tuning

#### High Memory Usage
Adjust retention settings in:
- `monitoring/prometheus/prometheus.yml` (storage.tsdb.retention.time)
- `monitoring/loki/loki.yml` (retention policies)

#### High Disk Usage
Configure log rotation:
- Prometheus data retention
- Loki log retention
- Application log rotation (already configured)

## 📚 Best Practices

### Monitoring Strategy

1. **Start with the Golden Signals**:
   - Latency (response times)
   - Traffic (request rates)
   - Errors (error rates)
   - Saturation (resource utilization)

2. **Set Meaningful Alerts**:
   - Focus on symptoms, not causes
   - Alert on user-impacting issues
   - Avoid alert fatigue

3. **Use Dashboards Effectively**:
   - Start with overview, drill down to details
   - Include both technical and business metrics
   - Make dashboards actionable

### Development Workflow

1. **Local Development**:
   ```bash
   make start-observability  # Start full stack
   make run                  # Start Weather MCP in another terminal
   ```

2. **Testing Changes**:
   ```bash
   make health-check         # Verify service health
   make metrics-check        # Check metrics format
   ```

3. **Debugging Issues**:
   ```bash
   make observability-logs   # View all service logs
   # Check correlation IDs in logs to trace requests
   ```

## 🚀 Production Deployment

### Security Considerations

1. **Authentication**: Configure Grafana with proper authentication
2. **Network Security**: Use proper firewall rules and VPNs
3. **Secrets Management**: Use proper secret management for alert webhooks
4. **TLS**: Enable TLS for all external connections

### Scaling Considerations

1. **Prometheus**: Consider federation for multiple instances
2. **Grafana**: Use external database for HA setups
3. **Loki**: Configure object storage for large deployments
4. **Resource Limits**: Set appropriate CPU/memory limits

### Backup Strategy

1. **Prometheus Data**: Regular snapshots of TSDB
2. **Grafana Dashboards**: Export dashboards and datasources
3. **Configuration**: Version control all configuration files

## 🔗 Useful Commands

```bash
# Quick start
make start-observability

# Status checks
make observability-status
make health-check
make metrics-check

# Management
make observability-up
make observability-down
make observability-restart
make observability-logs

# Open tools
make grafana-open
make prometheus-open

# Development
docker-compose -f docker-compose.observability.yml --profile dev up
```

## 📞 Support

For observability-related issues:

1. Check the troubleshooting section above
2. Review service logs: `make observability-logs`
3. Verify configuration files in `monitoring/` directory
4. Check Docker container status: `docker ps`

The observability stack provides comprehensive monitoring for the Weather MCP service, enabling proactive issue detection and performance optimization.
