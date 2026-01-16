# SearchFlow - Technology Stack

## Programming Languages

### Python 3.12+
**Primary backend language**
- Modern async/await support
- Type hints and static typing
- Rich ecosystem for AI/ML
- FastAPI compatibility

### TypeScript
**Frontend language**
- Type-safe React development
- Next.js integration
- Enhanced IDE support

## Core Frameworks

### Backend: FastAPI
**Version:** 0.104.0+
**Purpose:** High-performance async web framework

**Key Features:**
- Automatic OpenAPI documentation
- Pydantic integration for validation
- Async/await native support
- Type hints for IDE support

**Usage:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8007 --reload
```

### Frontend: Next.js 14+
**Purpose:** React framework with App Router

**Key Features:**
- Server-side rendering
- App Router architecture
- TypeScript support
- Tailwind CSS integration

**Usage:**
```bash
npm run dev  # Development server
npm run build  # Production build
```

## AI/ML Stack

### DSPy 2.0+
**Purpose:** AI reasoning and prompt optimization

**Key Features:**
- Structured output generation
- Multi-LLM provider support
- Signature-based programming
- Automatic prompt optimization

**Usage in Project:**
- Search result processing
- Information extraction
- Structured data generation

### LLM Providers

#### 1. Google Gemini
**Model:** gemini-2.0-flash-lite
**Best for:** Free tier with high quality
**Configuration:**
- API Key: `GEMINI_API_KEY`
- Max tokens: 1000
- Temperature: 0.3

#### 2. Groq
**Model:** llama-3.1-8b-instant
**Best for:** Fast inference
**Limits:** 30 req/min, 6000 tokens/min (free tier)
**Configuration:**
- API Key: `GROQ_API_KEY`
- Max tokens: 500
- Temperature: 0.3

#### 3. Ollama
**Model:** llama2 (configurable)
**Best for:** Local/offline deployment
**Configuration:**
- Base URL: `http://localhost:11434`
- Max tokens: 1000
- Temperature: 0.3

#### 4. OpenAI (Legacy)
**Model:** gpt-4o-mini
**Best for:** High-quality results
**Configuration:**
- API Key: `OPENAI_API_KEY`

## Search Engine

### SearXNG
**Purpose:** Privacy-respecting metasearch engine

**Key Features:**
- Multi-engine aggregation (Google, Bing, DuckDuckGo)
- No tracking or ads
- Self-hosted
- JSON API

**Configuration:**
- URL: `http://localhost:8888`
- Settings: `searxng/settings.yml`
- Limiter: `searxng/limiter.toml`

**Docker Image:** `searxng/searxng:latest`

## Data & Caching

### Redis 7
**Purpose:** High-performance caching layer

**Key Features:**
- In-memory data store
- Persistence with AOF
- Pub/sub capabilities
- Health checks

**Configuration:**
- Port: 6380 (external), 6379 (internal)
- Persistence: Append-only file
- Health check: `redis-cli ping`

**Docker Image:** `redis:7-alpine`

## Core Dependencies

### HTTP & Networking
- **httpx** (0.25.0+) - Async HTTP client
- **requests** (2.31.0+) - Sync HTTP client
- **uvicorn[standard]** (0.24.0+) - ASGI server

### Data Validation & Serialization
- **pydantic** (2.0.0+) - Data validation
- **pydantic-settings** (2.0.0+) - Settings management

### Environment & Configuration
- **python-dotenv** (1.0.0+) - Environment variable loading

### AI/ML
- **dspy-ai** (2.0.0+) - AI reasoning framework

## Development Dependencies

### Testing
- **pytest** (7.4.0+) - Test framework
- **pytest-asyncio** (0.21.0+) - Async test support
- **pytest-cov** (4.1.0+) - Coverage reporting

### Code Quality
- **black** (23.0.0+) - Code formatter
- **flake8** (6.0.0+) - Linter
- **isort** (5.12.0+) - Import sorter
- **mypy** (1.0.0+) - Static type checker
- **pre-commit** (3.0.0+) - Git hooks

## Build System

### UV Package Manager
**Purpose:** Fast Python package manager

**Key Commands:**
```bash
uv sync              # Install dependencies
uv add <package>     # Add dependency
uv run <command>     # Run command in venv
```

**Configuration:** `pyproject.toml`, `uv.lock`

### Hatchling
**Purpose:** Build backend for Python packages

**Configuration:**
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Containerization

### Docker
**Purpose:** Application containerization

**Key Files:**
- `docker/Dockerfile.api` - API service
- `docker/Dockerfile.searxng` - SearXNG service
- `frontend/Dockerfile` - Frontend service

### Docker Compose
**Version:** 3.8
**Purpose:** Multi-service orchestration

**Services:**
- api (port 8007)
- searxng (port 8888)
- redis (port 6380)
- frontend (port 3000)

**Commands:**
```bash
docker-compose up -d        # Start all services
docker-compose down         # Stop all services
docker-compose logs -f api  # View API logs
```

## CI/CD

### GitHub Actions
**Workflows:**
- `.github/workflows/build.yml` - Build verification
- `.github/workflows/lint.yml` - Code quality checks
- `.github/workflows/tests.yml` - Test execution

### Pre-commit Hooks
**Configuration:** `.pre-commit-config.yaml`

**Hooks:**
- Code formatting (black, isort)
- Linting (flake8)
- Type checking (mypy)

## Development Tools

### Makefile
**Purpose:** Common development commands

**Key Targets:**
```bash
make install    # Install dependencies
make test       # Run tests
make lint       # Run linters
make format     # Format code
make run        # Start development server
```

### Testing Scripts
- `test_llm_setup.sh` - Verify LLM configuration
- `test_searxng.py` - Test SearXNG integration
- `example_multi_llm.py` - Multi-LLM example

## Configuration Files

### Python
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Locked dependency versions
- `requirements.txt` - Pip-compatible dependencies
- `.python-version` - Python version specification

### Frontend
- `frontend/package.json` - Node.js dependencies
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/next.config.ts` - Next.js configuration
- `frontend/postcss.config.mjs` - PostCSS configuration
- `frontend/eslint.config.mjs` - ESLint configuration

### Docker
- `docker-compose.yml` - Service orchestration
- `.dockerignore` - Docker build exclusions

### Git
- `.gitignore` - Git exclusions
- `.pre-commit-config.yaml` - Pre-commit hooks

### Environment
- `.env` - Local environment variables
- `.env.example` - Environment template

## API Documentation

### OpenAPI/Swagger
**Endpoints:**
- `/docs` - Interactive Swagger UI
- `/redoc` - ReDoc documentation

**Features:**
- Auto-generated from FastAPI routes
- Interactive API testing
- Schema documentation

## Logging & Monitoring

### Logging
**Configuration:** `app/core/logging.py`

**Features:**
- Structured logging
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Request/response logging
- Error tracking

### Health Checks
**Endpoints:**
- `/` - Service status
- `/health` - Detailed health check with cache stats

## Performance Optimization

### Async/Await
- All I/O operations are async
- Non-blocking request handling
- High concurrency support

### Caching Strategy
- Redis for result caching
- Configurable TTL
- Cache statistics tracking
- Graceful degradation on cache failure

### Connection Pooling
- HTTP client connection reuse
- Redis connection pooling
- Efficient resource utilization

## Security

### CORS Configuration
**Middleware:** FastAPI CORSMiddleware
**Allowed Origins:** Configurable via `ALLOWED_ORIGINS`

### Environment Variables
- Sensitive data in `.env`
- Never committed to version control
- Template provided in `.env.example`

### API Keys
- LLM provider keys
- SearXNG secret key
- Stored in environment variables

## Deployment Requirements

### Minimum System Requirements
- Python 3.12+
- Docker & Docker Compose
- 2GB RAM minimum
- 10GB disk space

### Production Recommendations
- 4GB+ RAM
- Multi-core CPU
- SSD storage
- Reverse proxy (nginx/traefik)
- SSL/TLS certificates

## Version Control

### Git
**Repository Structure:**
- Main branch for stable releases
- Feature branches for development
- GitHub Actions for CI/CD

### Versioning
**Current Version:** 0.1.0
**Scheme:** Semantic Versioning (MAJOR.MINOR.PATCH)
