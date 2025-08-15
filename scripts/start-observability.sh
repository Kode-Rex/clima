#!/bin/bash

# Start Weather MCP Server with full observability stack
# This script starts Prometheus, Grafana, Loki, and all monitoring components

set -e

echo "🔍 Starting Weather MCP Observability Stack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Copy env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📋 Creating .env file from env.example..."
    cp env.example .env
fi

# Start the observability stack
echo "🚀 Starting observability stack with Docker Compose..."
docker-compose -f docker-compose.observability.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check Weather MCP service
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Weather MCP service is healthy"
else
    echo "⚠️ Weather MCP service is not responding"
fi

# Check Prometheus
if curl -f http://localhost:9091/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus is healthy"
else
    echo "⚠️ Prometheus is not responding"
fi

# Check Grafana
if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
    echo "✅ Grafana is healthy"
else
    echo "⚠️ Grafana is not responding"
fi

# Check Loki
if curl -f http://localhost:3100/ready > /dev/null 2>&1; then
    echo "✅ Loki is healthy"
else
    echo "⚠️ Loki is not responding"
fi

echo ""
echo "🎉 Observability stack is running!"
echo ""
echo "📊 Access your monitoring tools:"
echo "   Weather MCP API: http://localhost:8000"
echo "   Health Check: http://localhost:8000/health"
echo "   Metrics: http://localhost:8000/metrics"
echo "   Grafana Dashboard: http://localhost:3000 (admin/admin)"
echo "   Prometheus: http://localhost:9091"
echo "   AlertManager: http://localhost:9093"
echo ""
echo "📖 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.observability.yml logs -f"
echo "   Stop stack: docker-compose -f docker-compose.observability.yml down"
echo "   Restart: docker-compose -f docker-compose.observability.yml restart"
echo ""
echo "🔧 Test the API:"
echo "   curl http://localhost:8000/health"
echo "   curl http://localhost:8000/metrics"
echo ""
