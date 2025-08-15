"""
Observability infrastructure for Weather MCP Server
Includes metrics, tracing, and structured logging
"""

import time
import uuid
from collections.abc import Callable
from contextlib import contextmanager
from functools import wraps
from typing import Any

from loguru import logger
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Prometheus Metrics
API_REQUESTS_TOTAL = Counter(
    "weather_api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "status_code"],
)

API_REQUEST_DURATION = Histogram(
    "weather_api_request_duration_seconds",
    "Time spent processing API requests",
    ["method", "endpoint"],
)

NWS_API_REQUESTS_TOTAL = Counter(
    "nws_api_requests_total",
    "Total number of NWS API requests",
    ["endpoint", "status_code"],
)

NWS_API_REQUEST_DURATION = Histogram(
    "nws_api_request_duration_seconds", "Time spent on NWS API requests", ["endpoint"]
)

CACHE_OPERATIONS_TOTAL = Counter(
    "cache_operations_total",
    "Total cache operations",
    ["operation", "result"],  # operation: get/set, result: hit/miss/success/error
)

SSE_CONNECTIONS_ACTIVE = Gauge(
    "sse_connections_active", "Number of active SSE connections"
)

SSE_CONNECTIONS_TOTAL = Counter(
    "sse_connections_total",
    "Total SSE connections",
    ["status"],  # status: opened/closed/error
)

WEATHER_DATA_FRESHNESS = Gauge(
    "weather_data_freshness_seconds",
    "Age of weather data in seconds",
    ["location", "data_type"],
)

ERROR_COUNTER = Counter(
    "weather_errors_total", "Total number of errors", ["service", "error_type"]
)


class ObservabilityManager:
    """Central manager for observability features"""

    def __init__(self):
        self.tracer_provider = None
        self.meter_provider = None
        self.correlation_id: str | None = None

    def setup_tracing(self):
        """Setup OpenTelemetry tracing"""
        self.tracer_provider = TracerProvider()
        trace.set_tracer_provider(self.tracer_provider)

    def setup_metrics(self, prometheus_port: int = 9090):
        """Setup Prometheus metrics server"""
        try:
            start_http_server(prometheus_port)
            logger.info(f"Prometheus metrics server started on port {prometheus_port}")
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")

    def get_tracer(self, name: str):
        """Get a tracer instance"""
        return trace.get_tracer(name)

    def set_correlation_id(self, correlation_id: str | None = None):
        """Set correlation ID for request tracing"""
        self.correlation_id = correlation_id or str(uuid.uuid4())
        return self.correlation_id


# Global observability manager
observability = ObservabilityManager()


def track_api_request(endpoint: str, method: str = "GET"):
    """Decorator to track API request metrics"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            correlation_id = observability.set_correlation_id()

            try:
                # Start span for tracing
                tracer = observability.get_tracer(__name__)
                with tracer.start_as_current_span(f"{method} {endpoint}") as span:
                    span.set_attribute("correlation_id", correlation_id)
                    span.set_attribute("endpoint", endpoint)
                    span.set_attribute("method", method)

                    # Execute the function
                    result = await func(*args, **kwargs)

                    # Determine status code from result
                    status_code = "200" if result.get("success", True) else "500"
                    span.set_attribute("status_code", status_code)

                    # Record metrics
                    API_REQUESTS_TOTAL.labels(
                        method=method, endpoint=endpoint, status_code=status_code
                    ).inc()

                    duration = time.time() - start_time
                    API_REQUEST_DURATION.labels(
                        method=method, endpoint=endpoint
                    ).observe(duration)

                    # Structured logging
                    logger.info(
                        "API request completed",
                        extra={
                            "correlation_id": correlation_id,
                            "endpoint": endpoint,
                            "method": method,
                            "status_code": status_code,
                            "duration": duration,
                            "success": result.get("success", True),
                        },
                    )

                    return result

            except Exception as e:
                # Record error metrics
                API_REQUESTS_TOTAL.labels(
                    method=method, endpoint=endpoint, status_code="500"
                ).inc()

                ERROR_COUNTER.labels(service="api", error_type=type(e).__name__).inc()

                # Log error with correlation ID
                logger.error(
                    f"API request failed: {e}",
                    extra={
                        "correlation_id": correlation_id,
                        "endpoint": endpoint,
                        "method": method,
                        "error_type": type(e).__name__,
                        "duration": time.time() - start_time,
                    },
                )
                raise

        return wrapper

    return decorator


def track_nws_request(endpoint: str):
    """Decorator to track NWS API requests"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)

                # Record successful request
                NWS_API_REQUESTS_TOTAL.labels(
                    endpoint=endpoint, status_code="200"
                ).inc()

                duration = time.time() - start_time
                NWS_API_REQUEST_DURATION.labels(endpoint=endpoint).observe(duration)

                logger.debug(
                    f"NWS API request successful: {endpoint}",
                    extra={
                        "correlation_id": observability.correlation_id,
                        "nws_endpoint": endpoint,
                        "duration": duration,
                    },
                )

                return result

            except Exception as e:
                # Record failed request
                NWS_API_REQUESTS_TOTAL.labels(
                    endpoint=endpoint, status_code="500"
                ).inc()

                ERROR_COUNTER.labels(
                    service="nws_api", error_type=type(e).__name__
                ).inc()

                logger.error(
                    f"NWS API request failed: {endpoint} - {e}",
                    extra={
                        "correlation_id": observability.correlation_id,
                        "nws_endpoint": endpoint,
                        "error_type": type(e).__name__,
                        "duration": time.time() - start_time,
                    },
                )
                raise

        return wrapper

    return decorator


def track_cache_operation(operation: str):
    """Decorator to track cache operations"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # Determine cache result
                if operation == "get":
                    cache_result = "hit" if result is not None else "miss"
                else:  # set
                    cache_result = "success"

                CACHE_OPERATIONS_TOTAL.labels(
                    operation=operation, result=cache_result
                ).inc()

                logger.debug(
                    f"Cache {operation}: {cache_result}",
                    extra={
                        "correlation_id": observability.correlation_id,
                        "cache_operation": operation,
                        "cache_result": cache_result,
                    },
                )

                return result

            except Exception as e:
                CACHE_OPERATIONS_TOTAL.labels(operation=operation, result="error").inc()

                ERROR_COUNTER.labels(service="cache", error_type=type(e).__name__).inc()

                logger.error(
                    f"Cache {operation} failed: {e}",
                    extra={
                        "correlation_id": observability.correlation_id,
                        "cache_operation": operation,
                        "error_type": type(e).__name__,
                    },
                )
                raise

        return wrapper

    return decorator


@contextmanager
def track_sse_connection():
    """Context manager to track SSE connections"""
    SSE_CONNECTIONS_ACTIVE.inc()
    SSE_CONNECTIONS_TOTAL.labels(status="opened").inc()

    connection_id = str(uuid.uuid4())
    logger.info(
        "SSE connection opened",
        extra={
            "connection_id": connection_id,
            "active_connections": SSE_CONNECTIONS_ACTIVE._value._value,
        },
    )

    try:
        yield connection_id
    except Exception as e:
        SSE_CONNECTIONS_TOTAL.labels(status="error").inc()
        ERROR_COUNTER.labels(service="sse", error_type=type(e).__name__).inc()

        logger.error(
            f"SSE connection error: {e}",
            extra={"connection_id": connection_id, "error_type": type(e).__name__},
        )
        raise
    finally:
        SSE_CONNECTIONS_ACTIVE.dec()
        SSE_CONNECTIONS_TOTAL.labels(status="closed").inc()

        logger.info(
            "SSE connection closed",
            extra={
                "connection_id": connection_id,
                "active_connections": SSE_CONNECTIONS_ACTIVE._value._value,
            },
        )


def record_weather_data_freshness(location: str, data_type: str, timestamp: float):
    """Record weather data freshness metrics"""
    age_seconds = time.time() - timestamp
    WEATHER_DATA_FRESHNESS.labels(location=location, data_type=data_type).set(
        age_seconds
    )

    logger.debug(
        f"Weather data freshness recorded: {data_type} for {location}",
        extra={
            "correlation_id": observability.correlation_id,
            "location": location,
            "data_type": data_type,
            "age_seconds": age_seconds,
        },
    )


def setup_structured_logging():
    """Configure structured logging with JSON format"""
    import sys

    from loguru import logger

    # Remove default logger
    logger.remove()

    # Add structured JSON logger
    logger.add(
        sys.stderr,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {extra} | {message}",
        level="INFO",
        serialize=False,  # Keep human readable for now, can enable JSON later
        colorize=True,
    )

    # Add file logger for production
    logger.add(
        "logs/clima-mcp.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} | {extra} | {message}",
        level="DEBUG",
        rotation="100 MB",
        retention="7 days",
        compression="gz",
        serialize=True,  # JSON format for log aggregation
    )


def get_health_metrics() -> dict[str, Any]:
    """Get health check metrics"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "metrics": {
            "active_sse_connections": SSE_CONNECTIONS_ACTIVE._value._value,
            "total_api_requests": sum(
                metric.samples[0].value
                for metric in API_REQUESTS_TOTAL.collect()
                for sample in metric.samples
            ),
            "total_nws_requests": sum(
                metric.samples[0].value
                for metric in NWS_API_REQUESTS_TOTAL.collect()
                for sample in metric.samples
            ),
            "total_errors": sum(
                metric.samples[0].value
                for metric in ERROR_COUNTER.collect()
                for sample in metric.samples
            ),
        },
    }
