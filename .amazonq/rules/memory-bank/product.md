# SearchFlow - Product Overview

## Purpose
SearchFlow is a self-hosted, AI-powered search backend that transforms live web data into structured, trustworthy knowledge for both humans and AI systems. Instead of returning a list of links, SearchFlow searches the internet, processes results using AI reasoning, and returns clear answers in both JSON (for machines) and Markdown (for humans).

## Core Value Proposition
SearchFlow solves the fundamental problem of modern information retrieval by combining:
- **Live web search** - Up-to-date information from multiple search engines
- **AI reasoning** - Intelligent filtering and structuring of raw data
- **Dual output** - Machine-readable JSON and human-readable Markdown
- **Source grounding** - Prevents AI hallucinations by anchoring to real web sources

## Key Features

### 1. Natural Language Queries
Users can ask questions naturally without keyword optimization:
- "Best FastAPI practices"
- "Compare LangChain vs DSPy"
- "How does MCP work?"

### 2. Live Web Search (SearXNG)
- Searches multiple search engines simultaneously
- Privacy-friendly with no ads or tracking
- Self-hosted for complete control
- Ensures fresh and unbiased information

### 3. Tool-Based Architecture (MCP)
Search is exposed as a tool, not hardcoded logic:
- Agent-friendly design
- Easy to extend with new capabilities
- Ready for multi-tool AI systems
- Follows Model Context Protocol standards

### 4. AI Reasoning & Cleanup (DSPy)
The AI pipeline:
- Filters noise and duplicates from search results
- Extracts key insights and patterns
- Avoids hallucinations through grounding
- Produces structured, reliable results

### 5. Dual Output Format
**JSON (for machines):**
- APIs and automation pipelines
- AI agents and autonomous systems
- Databases and RAG systems
- Integration with other tools

**Markdown (for humans):**
- Easy-to-read summaries
- Documentation-ready format
- Reports and dashboards
- Knowledge base articles

### 6. Multi-Consumer Design
SearchFlow serves multiple audiences:
- Human users via UI or API
- AI agents and autonomous systems
- Internal tools and workflows
- Knowledge management systems

## Target Users

### Primary Users
- **AI/ML Engineers** - Building intelligent agents and RAG systems
- **Backend Developers** - Creating search-powered applications
- **Research Teams** - Conducting technical analysis and comparisons
- **DevOps Teams** - Self-hosting knowledge infrastructure

### Use Cases
- **AI Research Assistant** - Grounded, real-time information for AI systems
- **Backend for AI Agents** - Tool-based search for autonomous agents
- **RAG Preprocessing Engine** - Clean, structured data for vector databases
- **Internal Knowledge System** - Company-wide search and analysis
- **Technical Comparison Tool** - Automated technology evaluation

## Technical Capabilities

### Current Features
- FastAPI-based REST API
- SearXNG integration for multi-engine search
- DSPy-powered AI reasoning pipeline
- Redis caching for performance
- Multiple LLM provider support (Gemini, Groq, Ollama, OpenAI)
- Docker-based deployment
- MCP tool server integration
- Credibility scoring for sources
- Export to JSON and Markdown formats

### Architecture Highlights
- Modular, extensible design
- Async/await for high performance
- Type-safe with Pydantic schemas
- Comprehensive error handling
- Production-ready logging
- Health check endpoints
- CORS support for web integration

## Future Expansion Opportunities
- Source credibility scoring enhancements
- Citations and reference tracking
- Query decomposition for complex questions
- Advanced caching strategies
- Streaming response support
- User feedback loop integration
- Vector database integration
- Knowledge graph extraction
- Web UI dashboard
- Multi-language support

## One-Line Summary
SearchFlow is a self-hosted AI-powered search backend that transforms live web data into structured, trustworthy knowledge for humans and machines.
