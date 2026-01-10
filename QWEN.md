# SearchFlow Project Context

## Project Overview

SearchFlow is a self-hosted, AI-powered search backend that transforms live web data into structured, trustworthy knowledge for both humans and AI systems. Instead of returning a list of links, it searches the internet, cleans the results using AI reasoning, and returns clear answers in both JSON (for machines) and Markdown (for humans).

The project serves as a knowledge extraction system that grounds AI in real web data, producing structured, reusable results that serve both humans and machines as a foundation for intelligent systems.

## Architecture

The SearchFlow architecture consists of several key components working together:

1. **FastAPI** - Core API server and orchestration layer that handles HTTP requests/responses with high performance and native async support
2. **SearXNG** - Privacy-friendly meta search engine that queries multiple search engines without ads or tracking
3. **DSPy** - AI reasoning layer that cleans and structures search results, avoiding hallucinations and extracting key insights
4. **MCP (Model Context Protocol)** - Tool interface layer that exposes search as a callable tool for AI agents

### Data Flow
```
User / App / AI Agent
       ↓
    FastAPI
       ↓
  MCP Tool Server
       ↓
    SearXNG
 (Live Web Search)
       ↓
  DSPy Reasoning
       ↓
Structured Output
   ├── JSON (machines)
   └── Markdown (humans)
```

## Core Features

1. **Natural Language Queries** - Ask questions in human terms without keyword tricks
2. **Live Web Search** - Access fresh, up-to-date information from multiple sources
3. **Privacy-Friendly Meta Search** - No vendor lock-in with searches across multiple engines
4. **Tool-Based Architecture** - Designed to be agent-friendly and easily extensible
5. **AI Reasoning & Cleanup** - Filters noise and produces structured results
6. **Dual Output Format** - JSON for machines and Markdown for humans
7. **Multi-Consumer Design** - Serves humans, AI agents, and automation systems

## Project Structure

The intended project structure is organized as follows:

```
app/
├── main.py                 # FastAPI entry point
├── api/
│   └── search.py          # Search API endpoint
├── mcp/
│   └── search_tool.py     # MCP search tool interface
├── search/
│   └── searxng_client.py  # SearXNG HTTP client
├── ai/
│   └── dspy_pipeline.py   # DSPy reasoning pipeline
├── schemas/
│   └── search.py          # Data models
├── core/
│   ├── config.py          # Configuration
│   └── logging.py         # Logging setup
└── utils/
    └── text.py            # Text processing utilities
```

## Development Status

Currently, the project is in the early stages of development:
- Basic file structure is defined
- Comprehensive documentation exists explaining the architecture and vision
- Only a minimal `main.py` with a "Hello from searchflow!" function exists
- Dependencies are not yet defined in requirements.txt
- The pyproject.toml is present but has no dependencies listed

## Technologies Used

- **Backend**: FastAPI (high-performance ASGI framework with excellent schema validation)
- **Search**: SearXNG (privacy-friendly meta search engine)
- **AI Logic**: DSPy (schema-first AI reasoning with testable, deterministic outputs)
- **Tool Interface**: MCP (Model Context Protocol for agent-friendly tool access)
- **Infrastructure**: Docker and Docker Compose for consistent environments
- **Testing**: Pytest for validation
- **Data Formats**: JSON for machine consumption, Markdown for human readability

## Building and Running

The project is designed to be containerized using Docker:
- Docker Compose runs the API + SearXNG together
- For development: `docker-compose up --build`
- API will be available at http://localhost:8000
- Swagger UI at http://localhost:8000/docs
- Example API call: `curl -X POST http://localhost:8000/search -H "Content-Type: application/json" -d '{"query": "Best FastAPI practices"}'`

## Testing

The project is planned to use Pytest for:
- API health tests
- Search endpoint tests
- End-to-end integration tests

## Future Scope

Planned enhancements include:
- Source credibility scoring
- Citations and references
- Query decomposition for complex questions
- Caching layer for improved response times
- Streaming responses
- User feedback mechanisms
- Vector database integration for RAG applications
- Knowledge graph extraction
- Web UI dashboard

## Use Cases

- AI Research Assistant
- Backend for AI Agents
- RAG preprocessing engine
- Internal company knowledge systems
- Technical comparison and analysis tools
