.PHONY: help install install-dev test test-unit test-integration coverage lint format format-check type-check clean dev-setup pre-commit run run-test docker-build docker-run run-docker run-docker-dev docker-logs docker-stop

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
	@echo "  run-docker    Start Docker container in SSE mode"
	@echo "  run-docker-dev Start Docker container in development mode"
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
	python -m weather_mcp.cli test

run:
	python -m weather_mcp.cli run

# CI/CD friendly commands
ci-test: install-dev lint format-check type-check test coverage
	@echo "All CI checks passed!"

# Docker commands (if you add Docker later)
docker-build:
	docker build -t clima-mcp .

docker-run:
	docker run -p 8000:8000 clima-mcp

run-docker:
	docker-compose up -d clima-mcp

run-docker-dev:
	docker-compose --profile dev up clima-mcp-dev

docker-logs:
	docker-compose logs -f clima-mcp

docker-stop:
	docker-compose down
