.PHONY: help install test lint format clean run docker-build docker-up docker-down

help:
	@echo "SearchFlow Development Commands"
	@echo "================================"
	@echo "make install       - Install dependencies with uv"
	@echo "make test          - Run tests with coverage"
	@echo "make lint          - Run code quality checks"
	@echo "make format        - Format code with black and isort"
	@echo "make clean         - Remove generated files and caches"
	@echo "make run           - Run the application locally"
	@echo "make docker-build  - Build Docker image"
	@echo "make docker-up     - Start services with docker-compose"
	@echo "make docker-down   - Stop services"
	@echo "make pre-commit    - Install and run pre-commit hooks"

install:
	@echo "Installing dependencies..."
	uv pip install -e ".[dev]"
	uv pip install pre-commit

test:
	@echo "Running tests with coverage..."
	. .venv/bin/activate && pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

lint:
	@echo "Running code quality checks..."
	. .venv/bin/activate && black --check app/ tests/
	. .venv/bin/activate && isort --check-only app/ tests/
	. .venv/bin/activate && flake8 app/ tests/ --max-line-length=100
	. .venv/bin/activate && mypy app/ --ignore-missing-imports

format:
	@echo "Formatting code..."
	. .venv/bin/activate && black app/ tests/
	. .venv/bin/activate && isort app/ tests/

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .coverage coverage.xml

run:
	@echo "Starting SearchFlow on port 8007..."
	uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting services..."
	docker-compose up -d

docker-down:
	@echo "Stopping services..."
	docker-compose down

pre-commit:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Running pre-commit on all files..."
	. .venv/bin/activate && pre-commit run --all-files
