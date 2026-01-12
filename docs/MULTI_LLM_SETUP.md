# Multi-LLM Provider Setup Guide

SearchFlow now supports multiple LLM providers! Switch between them by just changing one environment variable.

## Supported Providers

- **Groq** - Fast, free tier (30 req/min, 6000 tokens/min)
- **Google Gemini** - Best free tier, powerful models
- **Ollama** - Run models locally, completely free
- **OpenAI** - Original provider (legacy support)

## Quick Start

### 1. Configure Your Provider in `.env`

Simply uncomment the provider you want to use:

```env
# Choose ONE provider (uncomment the line you want)
LLM_PROVIDER=groq
# LLM_PROVIDER=gemini
# LLM_PROVIDER=ollama
```

### 2. Provider-Specific Configuration

#### Using Groq (Default - Recommended)

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.1-8b-instant
GROQ_MAX_TOKENS=500
GROQ_TEMPERATURE=0.3
```

**Get API Key:** https://console.groq.com (free)
**Free Tier:** 30 requests/min, 6000 tokens/min
**Models Available:**

- `llama-3.1-8b-instant` (fastest, smallest)
- `llama-3.1-70b-versatile` (more powerful)
- `mixtral-8x7b-32768` (long context)

#### Using Google Gemini

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy_your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-lite
GEMINI_MAX_TOKENS=1000
GEMINI_TEMPERATURE=0.3
```

**Get API Key:** https://makersuite.google.com/app/apikey (free)
**Free Tier:** 60 requests/min, 1M tokens/day
**Models Available:**

- `gemini-2.0-flash-lite` (fastest, free)
- `gemini-2.0-flash-exp` (experimental)
- `gemini-1.5-pro` (most powerful)

#### Using Ollama (Local)

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2
OLLAMA_MAX_TOKENS=1000
OLLAMA_TEMPERATURE=0.3
```

**Setup Ollama:**

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. Start Ollama: `ollama serve`

**Models Available:**

- `llama2` (good all-around)
- `mistral` (fast, efficient)
- `codellama` (code-focused)
- `phi` (small, fast)

#### Using OpenAI (Legacy)

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

**Get API Key:** https://platform.openai.com/api-keys
**Pricing:** Pay-per-token (~$0.15/1M input tokens)

## Switching Providers

Just change one line in `.env`:

```bash
# Switch to Groq
sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=groq/' .env

# Switch to Gemini
sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=gemini/' .env

# Switch to Ollama
sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env
```

Or manually edit [.env](.env) and change `LLM_PROVIDER=...`

## Testing Your Setup

### Test with curl:

```bash
curl -X POST http://localhost:8007/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "what is python programming"}'
```

### Check logs to see which provider is being used:

```bash
make logs
# Look for: "Initializing LLM provider: groq"
```

## Troubleshooting

### Issue: "API key not set"

**Solution:** Make sure the API key for your chosen provider is set in `.env`

```bash
# Check your .env file
grep -E "GROQ_API_KEY|GEMINI_API_KEY|OLLAMA_BASE_URL" .env
```

### Issue: "Unknown LLM provider"

**Solution:** Verify `LLM_PROVIDER` is set to: `groq`, `gemini`, `ollama`, or `openai`

```bash
grep "LLM_PROVIDER" .env
```

### Issue: Ollama connection refused

**Solution:** Make sure Ollama is running

```bash
# Start Ollama
ollama serve

# Pull a model
ollama pull llama2

# Verify it's running
curl http://localhost:11434/api/tags
```

### Issue: Rate limit errors (Groq/Gemini)

**Solution:** Reduce request frequency or tokens:

```env
# For Groq
GROQ_MAX_TOKENS=300  # Reduce from 500

# For Gemini
GEMINI_MAX_TOKENS=500  # Reduce from 1000
```

## Provider Comparison

| Provider | Cost | Speed    | Free Tier            | Best For              |
| -------- | ---- | -------- | -------------------- | --------------------- |
| Groq     | Free | ⚡ Ultra | 30 req/min           | Production, fast apps |
| Gemini   | Free | ⚡ Fast  | 60 req/min, 1M tok/d | High volume           |
| Ollama   | Free | 🐢 Slow  | Unlimited (local)    | Privacy, offline      |
| OpenAI   | Paid | ⚡ Fast  | None                 | Best quality          |

## Recommended Settings

### For Development:

```env
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-8b-instant
GROQ_MAX_TOKENS=500
```

### For Production (High Volume):

```env
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-2.0-flash-lite
GEMINI_MAX_TOKENS=1000
```

### For Privacy/Offline:

```env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama2
OLLAMA_BASE_URL=http://localhost:11434
```

## Example Usage

### Python (Direct):

```python
from app.ai.dspy_pipeline import DSPyPipeline

# Initialize with current provider from .env
pipeline = DSPyPipeline()

# Search and answer
result = pipeline.search_and_answer("What is machine learning?")
print(result["answer"])
```

### API (HTTP):

```bash
curl -X POST http://localhost:8007/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "explain quantum computing",
    "include_context": true
  }'
```

## Advanced: Override Model at Runtime

You can override the model without changing `.env`:

```python
from app.ai.dspy_pipeline import DSPyPipeline

# Use a different Groq model
pipeline = DSPyPipeline(lm_model="llama-3.1-70b-versatile")

# Or switch Gemini model
pipeline = DSPyPipeline(lm_model="gemini-1.5-pro")
```

## Summary

✅ **To switch providers:** Change `LLM_PROVIDER` in `.env`
✅ **No code changes needed:** Everything is automatic
✅ **All providers work the same:** Same API, same results
✅ **Free options available:** Groq, Gemini, and Ollama are free

---

**Need help?** Check the logs: `make logs` or `docker-compose logs -f api`
