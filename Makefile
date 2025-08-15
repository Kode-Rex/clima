.PHONY: help install install-dev test test-unit test-integration coverage lint format format-check type-check clean dev-setup pre-commit run run-test docker-build docker-run docker-dev-run docker-logs docker-stop

# Default target
help:
	@echo "Available commands:"
	@echo "  install       Install production dependencies"
	@echo "  install-dev   Install development dependencies"
	@echo "  dev-setup     Full development environment setup"
	@echo "  test          Run all tests"
	@echo "  test-unit     Run unit tests only"
	@echo "  test-integration  Run integration tests only"
	@echo "  coverage      Run tests with coverage"
	@echo "  lint          Run linting (ruff)"
	@echo "  format        Format code (black + ruff)"
	@echo "  type-check    Run type checking (mypy)"
	@echo "  pre-commit    Run pre-commit hooks"
	@echo "  clean         Clean up build artifacts"
	@echo "  run-test      Test the NWS API"
	@echo "  run           Run weather API server"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-run    Start Docker container with docker-compose"
	@echo "  docker-dev-run Start Docker container in development mode"
	@echo "  docker-logs   View Docker container logs"
	@echo "  docker-stop   Stop Docker containers"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

dev-setup: install-dev
	pre-commit install
	@echo "Development environment setup complete!"

test:
	python -m pytest tests/ -v

test-unit:
	python -m pytest tests/ -m unit -v

test-integration:
	python -m pytest tests/ -m integration -v

coverage:
	python -m pytest tests/ --cov=weather_mcp --cov-report=term-missing --cov-report=html

lint:
	ruff check weather_mcp/ tests/ main.py

format:
	black weather_mcp/ tests/ main.py
	ruff check --fix weather_mcp/ tests/ main.py

format-check:
	black --check weather_mcp/ tests/ main.py

type-check:
	mypy --ignore-missing-imports weather_mcp/ main.py

pre-commit:
	pre-commit run --all-files

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/

# Application commands
run-test:
	@if [ -f venv/bin/python ]; then \
		venv/bin/python -m weather_mcp.cli test; \
	else \
		python -m weather_mcp.cli test; \
	fi

run:
	@if [ -f venv/bin/python ]; then \
		venv/bin/python -m weather_mcp.cli run; \
	else \
		python -m weather_mcp.cli run; \
	fi

# CI/CD friendly commands
ci-test: install-dev lint format-check type-check test coverage
	@echo "All CI checks passed!"

# Docker commands (if you add Docker later)
docker-build:
	docker build -t clima-mcp .

docker-run:
	docker-compose up -d clima-mcp

docker-dev-run:
	docker-compose --profile dev up clima-mcp-dev

docker-logs:
	docker-compose logs -f clima-mcp

docker-stop:
	docker-compose down

# =============================================================================
# OBSERVABILITY
# =============================================================================

start-observability:
	@echo "🔍 Starting full observability stack..."
	./scripts/start-observability.sh

observability-up:
	docker-compose -f docker-compose.observability.yml up -d

observability-down:
	docker-compose -f docker-compose.observability.yml down

observability-logs:
	docker-compose -f docker-compose.observability.yml logs -f

observability-restart:
	docker-compose -f docker-compose.observability.yml restart

grafana-open:
	@echo "Opening Grafana dashboard..."
	@open http://localhost:3000 || echo "Visit http://localhost:3000 (admin/admin)"

prometheus-open:
	@echo "Opening Prometheus..."
	@open http://localhost:9091 || echo "Visit http://localhost:9091"

health-check:
	@echo "🏥 Checking service health..."
	@curl -s http://localhost:8001/health | jq . || echo "Service not responding"

metrics-check:
	@echo "📊 Checking metrics..."
	@curl -s http://localhost:8001/metrics | head -20

observability-status:
	@echo "📊 Observability Stack Status:"
	@echo "Weather MCP: $$(curl -s -o /dev/null -w "%%{http_code}" http://localhost:8001/health || echo "DOWN")"
	@echo "Prometheus: $$(curl -s -o /dev/null -w "%%{http_code}" http://localhost:9091/-/healthy || echo "DOWN")"
	@echo "Grafana: $$(curl -s -o /dev/null -w "%%{http_code}" http://localhost:3000/api/health || echo "DOWN")"
	@echo "Loki: $$(curl -s -o /dev/null -w "%%{http_code}" http://localhost:3100/ready || echo "DOWN")"
