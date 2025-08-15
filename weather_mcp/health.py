"""
Health check and metrics endpoints for Weather MCP Server
"""

import time
from pathlib import Path

from fastapi import FastAPI, Response
from fastapi.responses import HTMLResponse, JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .config import get_config
from .observability import get_health_metrics, observability


def setup_health_endpoints(app: FastAPI):
    """Setup health check and metrics endpoints"""

    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            health_data = get_health_metrics()
            return JSONResponse(status_code=200, content=health_data)
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "timestamp": time.time(),
                    "error": str(e),
                },
            )

    @app.get("/health/ready")
    async def readiness_check():
        """Readiness check endpoint"""
        try:
            # Check if observability is properly configured
            config = get_config()

            checks = {
                "observability": observability is not None,
                "metrics_enabled": config.enable_metrics,
                "tracing_enabled": config.enable_tracing,
            }

            all_ready = all(checks.values())

            return JSONResponse(
                status_code=200 if all_ready else 503,
                content={
                    "status": "ready" if all_ready else "not_ready",
                    "timestamp": time.time(),
                    "checks": checks,
                },
            )
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "not_ready",
                    "timestamp": time.time(),
                    "error": str(e),
                },
            )

    @app.get("/health/live")
    async def liveness_check():
        """Liveness check endpoint"""
        return JSONResponse(
            status_code=200,
            content={
                "status": "alive",
                "timestamp": time.time(),
                "service": "weather-mcp",
                "version": "0.2.0",
            },
        )

    @app.get("/metrics")
    async def prometheus_metrics():
        """Prometheus metrics endpoint"""
        try:
            metrics_data = generate_latest()
            return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to generate metrics", "details": str(e)},
            )

    @app.get("/metrics/custom")
    async def custom_metrics():
        """Custom application metrics endpoint"""
        try:
            return JSONResponse(status_code=200, content=get_health_metrics())
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to get custom metrics", "details": str(e)},
            )

    @app.get("/client")
    async def sse_client():
        """Serve the SSE test client"""
        try:
            # Get the path to the examples directory
            current_dir = Path(__file__).parent
            client_path = current_dir.parent / "examples" / "sse_client_real.html"

            if client_path.exists():
                # Read the HTML content and return it directly
                html_content = client_path.read_text(encoding="utf-8")
                return HTMLResponse(content=html_content)
            else:
                return JSONResponse(
                    status_code=404,
                    content={
                        "error": "SSE client file not found",
                        "path": str(client_path),
                    },
                )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"error": "Failed to serve SSE client", "details": str(e)},
            )


def create_health_app() -> FastAPI:
    """Create a standalone FastAPI app for health checks"""
    app = FastAPI(
        title="Weather MCP Health Service",
        description="Health checks and metrics for Weather MCP Server",
        version="0.2.0",
    )

    setup_health_endpoints(app)
    return app
