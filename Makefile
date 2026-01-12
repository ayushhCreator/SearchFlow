.PHONY: help install test lint format clean run docker-build docker-up docker-down docker-restart restart logs health status commit-ready frontend-dev frontend-build mcp-server

help:
	@echo "SearchFlow Development Commands"
	@echo "================================"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install dependencies with uv"
	@echo "  make run           - Run the API locally (port 8007)"
	@echo "  make frontend-dev  - Run frontend dev server (port 3000)"
	@echo "  make mcp-server    - Run MCP server for AI agents"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build  - Build all Docker images"
	@echo "  make docker-up     - Start all services (API, SearXNG, Redis, Frontend)"
	@echo "  make docker-down   - Stop all services"
	@echo "  make restart       - Restart all services"
	@echo "  make logs          - View service logs"
	@echo "  make health        - Check all services health"
	@echo "  make status        - Check service status"
	@echo ""
	@echo "Quality:"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run code quality checks"
	@echo "  make format        - Format code with black and isort"
	@echo "  make clean         - Remove generated files and caches"
	@echo "  make commit-ready  - Format, lint, and test before commit"

install:
	@echo "Installing dependencies..."
	uv pip install -e ".[dev]"
	uv pip install pre-commit
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

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
	rm -rf frontend/.next frontend/out

run:
	@echo "Starting SearchFlow API on port 8007..."
	. .venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload

frontend-dev:
	@echo "Starting frontend dev server on port 3000..."
	cd frontend && npm run dev

frontend-build:
	@echo "Building frontend for production..."
	cd frontend && npm run build

mcp-server:
	@echo "Starting MCP server for AI agents..."
	. .venv/bin/activate && python -m app.mcp.mcp_server

docker-build:
	@echo "Building Docker images..."
	docker-compose build

docker-up:
	@echo "Starting all services..."
	docker-compose up -d
	@echo ""
	@echo "✅ Services starting..."
	@echo "   API:      http://localhost:8007"
	@echo "   Frontend: http://localhost:3000"
	@echo "   SearXNG:  http://localhost:8888"
	@echo "   Redis:    localhost:6380"

docker-down:
	@echo "Stopping services..."
	docker-compose down

docker-restart:
	@echo "Restarting services..."
	docker-compose restart

restart: docker-restart
	@echo "✅ Services restarted"

logs:
	@echo "Showing service logs (Ctrl+C to exit)..."
	docker-compose logs -f

health:
	@echo "Checking service health..."
	@echo ""
	@echo "🔍 SearXNG:"
	@curl -s http://localhost:8888 > /dev/null && echo "  ✅ Running at http://localhost:8888" || echo "  ❌ Not responding"
	@echo ""
	@echo "🚀 API:"
	@curl -s http://localhost:8007/health > /dev/null && echo "  ✅ Running at http://localhost:8007" || echo "  ❌ Not responding"
	@echo ""
	@echo "🎨 Frontend:"
	@curl -s http://localhost:3000 > /dev/null && echo "  ✅ Running at http://localhost:3000" || echo "  ❌ Not responding"
	@echo ""
	@echo "💾 Redis:"
	@redis-cli -p 6380 ping > /dev/null 2>&1 && echo "  ✅ Running on port 6380" || echo "  ❌ Not responding (or redis-cli not installed)"
	@echo ""
	@echo "📊 API Details:"
	@curl -s http://localhost:8007/health | python3 -m json.tool 2>/dev/null || echo "  ⚠️  Could not get detailed health info"

status:
	@echo "Service Status:"
	@docker-compose ps

pre-commit:
	@echo "Installing pre-commit hooks..."
	pre-commit install
	@echo "Running pre-commit on all files..."
	. .venv/bin/activate && pre-commit run --all-files

commit-ready: format lint test
	@echo "✅ Ready to commit!"
