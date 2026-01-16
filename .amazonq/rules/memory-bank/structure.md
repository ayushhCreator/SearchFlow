# SearchFlow - Project Structure

## Directory Organization

```
SearchFlow/
├── app/                    # Main Python application
│   ├── ai/                # AI reasoning and LLM integration
│   ├── api/               # FastAPI routes and models
│   ├── cache/             # Redis caching layer
│   ├── core/              # Core configuration and logging
│   ├── mcp/               # Model Context Protocol server
│   ├── output/            # Output formatters (JSON/Markdown)
│   ├── schemas/           # Pydantic data models
│   ├── search/            # Search engine integration
│   ├── services/          # Business logic layer
│   ├── utils/             # Utility functions
│   └── main.py            # FastAPI application entry point
├── frontend/              # Next.js web interface
│   ├── app/               # Next.js app directory
│   └── public/            # Static assets
├── tests/                 # Test suite
├── docs/                  # Project documentation
├── DOCS2/                 # Additional documentation
├── docker/                # Docker configuration files
├── searxng/               # SearXNG configuration
└── .amazonq/              # Amazon Q rules and memory bank
```

## Core Components

### 1. AI Layer (`app/ai/`)
**Purpose:** AI reasoning and LLM provider abstraction

- `llm_providers.py` - Multi-provider LLM support (Gemini, Groq, Ollama, OpenAI)
- `pipeline.py` - DSPy reasoning pipeline for search result processing
- `signatures.py` - DSPy signature definitions for structured outputs

**Responsibilities:**
- Abstract LLM provider differences
- Process raw search results with AI reasoning
- Generate structured outputs from unstructured data
- Handle token limits and rate limiting

### 2. API Layer (`app/api/`)
**Purpose:** HTTP interface and request/response handling

- `routes.py` - Main search API endpoints
- `exports.py` - Export functionality (JSON/Markdown)
- `models.py` - API request/response models

**Responsibilities:**
- Define REST API endpoints
- Validate incoming requests
- Format API responses
- Handle HTTP errors

### 3. Cache Layer (`app/cache/`)
**Purpose:** Performance optimization through Redis caching

- `redis_client.py` - Redis connection and cache operations

**Responsibilities:**
- Cache search results
- Manage cache lifecycle
- Provide cache statistics
- Handle cache failures gracefully

### 4. Core Layer (`app/core/`)
**Purpose:** Application configuration and infrastructure

- `config.py` - Environment-based configuration management
- `logging.py` - Structured logging setup

**Responsibilities:**
- Load and validate environment variables
- Configure application settings
- Setup logging infrastructure
- Manage application lifecycle

### 5. MCP Layer (`app/mcp/`)
**Purpose:** Model Context Protocol integration

- `mcp_server.py` - MCP server implementation
- `search_tool.py` - Search tool definition for MCP

**Responsibilities:**
- Expose search as a tool for AI agents
- Follow MCP protocol standards
- Enable agent-to-agent communication
- Support tool composition

### 6. Output Layer (`app/output/`)
**Purpose:** Format results for different consumers

- `json_formatter.py` - Machine-readable JSON output
- `markdown_formatter.py` - Human-readable Markdown output

**Responsibilities:**
- Transform search results to JSON
- Generate formatted Markdown reports
- Maintain consistent output structure
- Support multiple export formats

### 7. Schema Layer (`app/schemas/`)
**Purpose:** Type-safe data models

- `search.py` - Search request/response schemas

**Responsibilities:**
- Define data structures with Pydantic
- Validate data at runtime
- Provide type hints for IDE support
- Document data contracts

### 8. Search Layer (`app/search/`)
**Purpose:** Search engine integration and result processing

- `searxng_client.py` - SearXNG API client
- `dspy_retriever.py` - DSPy-based search retrieval
- `credibility.py` - Source credibility scoring

**Responsibilities:**
- Interface with SearXNG
- Retrieve and parse search results
- Score source credibility
- Handle search engine errors

### 9. Services Layer (`app/services/`)
**Purpose:** Business logic orchestration

- `search.py` - Main search service orchestration
- `suggestions.py` - Search suggestion generation

**Responsibilities:**
- Coordinate between layers
- Implement business logic
- Manage service workflows
- Handle cross-cutting concerns

### 10. Frontend (`frontend/`)
**Purpose:** Web-based user interface

- Next.js 14+ with App Router
- TypeScript for type safety
- Tailwind CSS for styling
- React components for UI

**Responsibilities:**
- Provide web interface for search
- Display results in user-friendly format
- Handle user interactions
- Communicate with backend API

## Architectural Patterns

### Layered Architecture
The application follows a clean layered architecture:
1. **API Layer** - HTTP interface
2. **Service Layer** - Business logic
3. **Integration Layer** - External services (SearXNG, LLMs)
4. **Data Layer** - Caching and persistence

### Dependency Injection
- Configuration injected via environment variables
- Services receive dependencies through constructors
- Enables testing and modularity

### Async/Await Pattern
- All I/O operations are asynchronous
- Improves throughput and responsiveness
- Leverages FastAPI's async capabilities

### Provider Pattern
- Multiple LLM providers with unified interface
- Easy to add new providers
- Runtime provider selection

### Tool-Based Design
- Search exposed as MCP tool
- Composable with other tools
- Agent-friendly architecture

## Data Flow

```
User Request
    ↓
FastAPI Router (app/api/routes.py)
    ↓
Service Layer (app/services/search.py)
    ↓
Cache Check (app/cache/redis_client.py)
    ↓ (cache miss)
SearXNG Client (app/search/searxng_client.py)
    ↓
Raw Search Results
    ↓
DSPy Pipeline (app/ai/pipeline.py)
    ↓
LLM Provider (app/ai/llm_providers.py)
    ↓
Structured Results
    ↓
Output Formatter (app/output/)
    ↓
JSON + Markdown Response
    ↓
Cache Store
    ↓
Return to User
```

## Configuration Management

### Environment Variables
- `.env` - Local development configuration
- `.env.example` - Template for environment setup
- `app/core/config.py` - Pydantic Settings for validation

### Docker Configuration
- `docker-compose.yml` - Multi-service orchestration
- `docker/Dockerfile.api` - API service container
- `docker/Dockerfile.searxng` - SearXNG container

### Build Configuration
- `pyproject.toml` - Python project metadata and dependencies
- `uv.lock` - Locked dependency versions
- `requirements.txt` - Pip-compatible dependencies

## Testing Structure

```
tests/
├── test_health.py              # Health check tests
├── test_search_api.py          # API endpoint tests
├── test_searxng_integration.py # SearXNG integration tests
├── test_dspy_pipeline.py       # AI pipeline tests
├── test_multi_llm.py           # Multi-LLM provider tests
└── test_e2e.py                 # End-to-end tests
```

## Deployment Architecture

### Docker Compose Services
1. **api** - FastAPI application (port 8007)
2. **searxng** - Search engine (port 8888)
3. **redis** - Cache layer (port 6380)
4. **frontend** - Next.js UI (port 3000)

### Service Dependencies
- API depends on SearXNG and Redis
- Frontend depends on API
- All services networked via Docker

### Volume Management
- `searxng-data` - SearXNG persistent data
- `redis-data` - Redis cache persistence
- Source code mounted for development

## Extension Points

### Adding New LLM Providers
1. Implement provider in `app/ai/llm_providers.py`
2. Add configuration in `app/core/config.py`
3. Update provider selection logic

### Adding New Output Formats
1. Create formatter in `app/output/`
2. Implement formatting logic
3. Add export endpoint in `app/api/exports.py`

### Adding New Search Engines
1. Create client in `app/search/`
2. Implement search interface
3. Update service orchestration

### Adding New MCP Tools
1. Define tool in `app/mcp/`
2. Implement tool logic
3. Register with MCP server
