# SearchFlow - Development Guidelines

## Code Quality Standards

### Documentation Style
**Pattern:** Triple-quoted docstrings at module and function level
- **Module docstrings:** Brief description of module purpose and responsibility
- **Function docstrings:** Describe purpose, parameters, and return values
- **Single Responsibility Principle:** Explicitly stated in module docstrings

**Examples from codebase:**
```python
"""
DSPy Pipeline

Main search and reasoning pipeline.
Single Responsibility: Orchestrates search + AI reasoning.
"""

"""
Source Credibility Scoring

Assigns credibility scores to sources based on domain reputation.
Higher scores indicate more trustworthy sources.
"""
```

### Type Hints
**Pattern:** Comprehensive type annotations throughout
- Function parameters with types
- Return types specified
- Optional types for nullable values
- Generic types (List, Dict, Optional) from typing module

**Examples:**
```python
def get_credibility_score(url: str) -> tuple[float, str]:
    """Get credibility score for a URL."""

async def process_results(self, query: str, results: List[Dict]) -> Dict:
    """Process search results."""

class Settings(BaseSettings):
    ALLOWED_ORIGINS: Union[List[str], str] = "..."
```

### Naming Conventions
**Pattern:** Clear, descriptive names following Python conventions
- **Functions/methods:** snake_case with verb prefixes (get_, create_, handle_, process_)
- **Classes:** PascalCase with descriptive suffixes (Schema, Pipeline, Client, Retriever)
- **Constants:** UPPER_SNAKE_CASE for configuration and domain data
- **Private methods:** Leading underscore (_method_name)
- **Boolean variables:** Descriptive names (isLoading, showSidebar, cache_enabled)

**Examples:**
```python
# Functions with clear verb prefixes
def get_domain(url: str) -> str:
def enrich_with_credibility(sources: list[dict]) -> list[dict]:
def sort_by_credibility(sources: list[dict]) -> list[dict]:

# Private helper methods
def _rerank_passages(self, question: str, passages: List[str]) -> List[int]:
def _empty_result(self, question: str) -> Dict:
def _extract_confidence(self, result) -> float:
def _build_response(self, question: str, result, indices: List[int]) -> Dict:

# Classes with descriptive suffixes
class SearchRequestSchema(BaseModel):
class DSPyPipeline:
class SearXNGRetriever:
```

### Code Organization
**Pattern:** Logical grouping with clear separation of concerns
- Related constants grouped together with comments
- Helper functions separated from main logic
- Private methods prefixed with underscore
- Imports organized by category (standard library, third-party, local)

**Example from credibility.py:**
```python
# Domain reputation database
DOMAIN_SCORES: Dict[str, tuple[float, str]] = {
    # Official Documentation (0.95)
    "docs.python.org": (0.95, "official_docs"),
    # Academic & Research (0.93)
    "arxiv.org": (0.93, "academic"),
}

# Trusted TLD patterns
TRUSTED_TLDS = {
    ".edu": 0.90,
    ".gov": 0.92,
}
```

## Pydantic Patterns

### Schema Definition
**Pattern:** Comprehensive field definitions with validation and documentation
- Field() with descriptive parameters
- Validation constraints (min_length, max_length, ge, le)
- Default values where appropriate
- Config class with json_schema_extra for examples

**Example:**
```python
class SearchRequestSchema(BaseModel):
    query: str = Field(
        ..., min_length=1, max_length=500, description="Search query string"
    )
    limit: Optional[int] = Field(
        10, ge=1, le=50, description="Maximum number of results (1-50)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Best FastAPI practices",
                "limit": 10,
            }
        }
```

### Settings Management
**Pattern:** Pydantic Settings for environment-based configuration
- BaseSettings for automatic environment variable loading
- Type hints for all settings
- Default values provided
- Custom validators with @field_validator decorator
- Config class specifying .env file

**Example:**
```python
class Settings(BaseSettings):
    DEBUG: bool = False
    REDIS_URL: str = "redis://localhost:6380"
    CACHE_TTL: int = 3600

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
```

## Logging Patterns

### Logger Setup
**Pattern:** Module-level logger with descriptive messages
- Logger created at module level: `logger = logging.getLogger(__name__)`
- Emoji prefixes for visual categorization (✅, 🔍, 📝, ⚖️, 🧠)
- Structured log messages with context
- Different log levels (info, warning, error, debug)

**Examples:**
```python
logger = logging.getLogger(__name__)

logger.info(f"✅ LLM Ready | Model: {self._model_name}")
logger.info(f"🔍 Retrieved {len(passages)} passages in {retrieval_time:.2f}s")
logger.warning("Reranker returned no valid indices, using top by credibility")
logger.error(f"DSPy pipeline failed: {e}")
logger.debug(f"Enriched {len(sources)} sources with credibility scores")
```

### Performance Logging
**Pattern:** Time tracking for operations with detailed metrics
```python
start_retrieval = time.time()
passages = self.retriever(question)
retrieval_time = time.time() - start_retrieval
logger.info(f"🔍 Retrieved {len(passages)} passages in {retrieval_time:.2f}s")
```

## Error Handling

### Graceful Degradation
**Pattern:** Try-except blocks with fallback behavior
- Catch specific exceptions where possible
- Log errors with context
- Return sensible defaults
- Never expose internal errors to users

**Examples:**
```python
try:
    return float(result.confidence.split()[0])
except (ValueError, AttributeError, IndexError):
    return 0.7  # Sensible default

try:
    data = localStorage.getItem(STORAGE_KEY);
    return data ? JSON.parse(data) : [];
except (e) {
    console.error("Failed to load threads:", e);
    return [];  # Graceful fallback
}
```

### Error Response Pattern
**Pattern:** Structured error responses with helpful messages
```python
except Exception as e:
    logger.error(f"DSPy pipeline failed: {e}")
    return {
        "question": question,
        "answer": f"Error: {str(e)}",
        "context": [],
        "confidence": 0.0,
    }
```

## Async/Await Patterns

### Async Function Definitions
**Pattern:** Async functions for I/O operations
- Use async/await for network calls, database operations
- Maintain compatibility with sync code where needed
- Proper async context management

**Example:**
```python
async def process_results(self, query: str, results: List[Dict]) -> Dict:
    """Process search results (compatibility method)."""
    return self.search_and_answer(query)

async def health():
    """Health check endpoint."""
    cache = await get_cache_client()
    cache_stats = await cache.get_stats()
    return {"status": "healthy", "cache": cache_stats}
```

## React/TypeScript Patterns (Frontend)

### Component Structure
**Pattern:** Functional components with hooks
- "use client" directive for client components
- useState for local state management
- useEffect for side effects and lifecycle
- useRef for DOM references
- Custom helper functions outside component

**Example:**
```typescript
"use client";

export default function Home() {
  const [threads, setThreads] = useState<ChatThread[]>([]);
  const [currentThreadId, setCurrentThreadId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setThreads(loadThreads());
  }, []);
}
```

### Type Definitions
**Pattern:** Comprehensive TypeScript interfaces
- Interface definitions at top of file
- Optional properties with ? operator
- Union types for enums
- Descriptive property names

**Example:**
```typescript
interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  context?: Source[];
  confidence?: number;
  timestamp: number;
}

interface SearchState {
  status: "idle" | "searching" | "streaming" | "done" | "error";
  currentAnswer: string;
  error?: string;
}
```

### State Management
**Pattern:** Immutable state updates with spread operators
```typescript
setState(prev => ({ ...prev, currentAnswer: fullAnswer }));

setThreads(prev => prev.map(t => {
  if (t.id === threadId) {
    return { ...t, messages: [...t.messages, assistantMsg] };
  }
  return t;
}));
```

## API Design Patterns

### Streaming Responses
**Pattern:** Server-sent events for real-time updates
- Stream data in chunks
- Parse SSE format (data: prefix)
- Handle [DONE] marker
- Buffer incomplete messages

**Example:**
```typescript
const reader = response.body?.getReader();
const decoder = new TextDecoder();
let buffer = "";

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  buffer += decoder.decode(value, { stream: true });
  const lines = buffer.split("\n\n");
  buffer = lines.pop() || "";

  for (const line of lines) {
    const trimmed = line.replace(/^data: /, "").trim();
    if (!trimmed || trimmed === "[DONE]") continue;
    const event = JSON.parse(trimmed);
    // Process event
  }
}
```

### Configuration Constants
**Pattern:** Environment-based configuration with fallbacks
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8007";
const MAX_RETRIES = 3;
const STORAGE_KEY = "searchflow_threads";
```

## DSPy Integration Patterns

### Context Management
**Pattern:** Use dspy.context() for thread-safe LLM calls
```python
with dspy.context(lm=self._lm):
    result = self.answer(context=numbered_context[:3000], question=question)
```

### Signature-Based Programming
**Pattern:** Define signatures for structured outputs
```python
self.answer = dspy.ChainOfThought(SearchQA)
self.ranker = dspy.ChainOfThought(ContextRanker)
self.decomposer = dspy.ChainOfThought(QueryDecomposer)
```

### Pipeline Orchestration
**Pattern:** Multi-step processing with intermediate results
1. Retrieval - Get raw search results
2. Reranking - Score and filter by relevance + credibility
3. Synthesis - Generate answer with LLM
4. Response building - Structure output

**Example:**
```python
# Step 1: Retrieval
passages = self.retriever(question)

# Step 2: Reranking
selected_indices = self._rerank_passages(question, passages)

# Step 3: Synthesis
ranked_passages = [passages[i] for i in selected_indices]
numbered_context = "\n\n".join([f"[{idx}] {p}" for idx, p in enumerate(ranked_passages)])

with dspy.context(lm=self._lm):
    result = self.answer(context=numbered_context[:3000], question=question)

# Step 4: Response building
return self._build_response(question, result, selected_indices)
```

## Data Enrichment Patterns

### Credibility Scoring
**Pattern:** Enrich data with metadata through helper functions
```python
def enrich_with_credibility(sources: list[dict]) -> list[dict]:
    """Enrich source list with credibility scores."""
    enriched = []
    for source in sources:
        url = source.get("url", "")
        score, category = get_credibility_score(url)
        enriched.append({
            **source,
            "credibility_score": score,
            "credibility_category": category,
        })
    return enriched
```

### Domain Reputation Database
**Pattern:** Structured data with comments for maintainability
```python
DOMAIN_SCORES: Dict[str, tuple[float, str]] = {
    # Official Documentation (0.95)
    "docs.python.org": (0.95, "official_docs"),
    "fastapi.tiangolo.com": (0.95, "official_docs"),

    # Academic & Research (0.93)
    "arxiv.org": (0.93, "academic"),
}
```

## Testing Patterns

### Test Organization
**Pattern:** Descriptive test file names with test_ prefix
- test_health.py - Health check tests
- test_search_api.py - API endpoint tests
- test_searxng_integration.py - Integration tests
- test_dspy_pipeline.py - AI pipeline tests
- test_e2e.py - End-to-end tests

## Configuration Management

### Environment Variables
**Pattern:** .env file with comprehensive documentation
- Comments explaining each variable
- Grouped by category (SearXNG, LLM, FastAPI)
- Multiple provider options documented
- Sensible defaults provided

**Example:**
```bash
# LLM Provider: "ollama", "groq", or "gemini"
LLM_PROVIDER=groq

# Groq Free Tier Limits (to conserve quota)
# Free tier: 30 requests/min, 6000 tokens/min
GROQ_MODEL=llama-3.1-8b-instant
GROQ_MAX_TOKENS=500
```

## Performance Optimization

### Caching Strategy
**Pattern:** Check cache before expensive operations
```python
cache = await get_cache_client()
cache_stats = await cache.get_stats()
```

### Result Limiting
**Pattern:** Limit results early to avoid processing overhead
```python
k_results: int = 10  # Increased for reranking
selected_indices[:5]  # Limit to top 5 relevant
numbered_context[:3000]  # Truncate context to token limit
```

### Deduplication
**Pattern:** Remove duplicates by unique identifier
```python
seen_urls = set()
unique_raw = []
for raw, passage in zip(all_raw_results, all_passages):
    url = raw.get("url", "")
    if url not in seen_urls:
        seen_urls.add(url)
        unique_raw.append(raw)
```

## Code Comments

### Inline Comments
**Pattern:** Step markers and explanatory comments
```python
# Step 1: Retrieval
passages = self.retriever(question)

# Step 2: Reranking
selected_indices = self._rerank_passages(question, passages)

# Fallback: sort by credibility and take top 3
sorted_by_cred = sorted(...)
```

### Section Comments
**Pattern:** Visual separators for major sections
```typescript
// --- Types ---
interface Message { ... }

// --- Helpers ---
function loadThreads() { ... }

// --- Main Component ---
export default function Home() { ... }
```

## Best Practices Summary

1. **Always use type hints** - Python and TypeScript both benefit from strong typing
2. **Document with docstrings** - Every module and public function should have clear documentation
3. **Log with context** - Include relevant metrics and use emoji prefixes for visual scanning
4. **Handle errors gracefully** - Never expose internal errors, always provide fallbacks
5. **Use descriptive names** - Function names should clearly indicate their purpose
6. **Separate concerns** - Private helper methods for complex logic
7. **Validate inputs** - Use Pydantic Field() with constraints
8. **Provide examples** - Include json_schema_extra in Pydantic models
9. **Optimize early** - Limit results, truncate context, deduplicate data
10. **Test thoroughly** - Organize tests by feature and integration level
