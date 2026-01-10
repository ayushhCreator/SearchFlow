# SearXNG Quick Start

Quick reference for getting SearXNG working with SearchFlow.

## 1️⃣ Start SearXNG

### With Docker Compose (Recommended)

```bash
make docker-up
```

Starts:

- API: http://localhost:8007
- SearXNG: http://localhost:8888

### Verify It's Running

```bash
curl http://localhost:8888
```

## 2️⃣ Test SearXNG Directly

### Simple Search

```bash
curl "http://localhost:8888/search?q=python&format=json"
```

### With More Options

```bash
curl "http://localhost:8888/search?q=fastapi&format=json&language=en&pageno=1"
```

## 3️⃣ Configure for SearchFlow

### Check Configuration

```bash
# View SearXNG status
docker logs searchflow-searxng-1

# Check configuration
curl http://localhost:8888/config
```

## 4️⃣ Use in Your Code

### Quick Example

```python
from app.search.searxng_client import SearXNGClient
import asyncio

async def main():
    client = SearXNGClient()
    results = await client.search("your query")
    print(results)
    await client.close()

asyncio.run(main())
```

### With Context Manager

```python
from app.search.searxng_client import SearXNGClient
import asyncio

async def main():
    async with SearXNGClient() as client:
        results = await client.search("your query")
        print(results)

asyncio.run(main())
```

## 5️⃣ Test Integration

```bash
# Run SearXNG tests
pytest tests/test_searxng_integration.py -v

# Run all tests
make test
```

## 6️⃣ Troubleshooting

| Issue              | Solution                                      |
| ------------------ | --------------------------------------------- |
| Connection refused | `make docker-up` to start SearXNG             |
| No results         | Check query syntax, try simple queries        |
| Slow responses     | Limit engines in configuration                |
| 503 error          | Restart: `make docker-down && make docker-up` |

## 7️⃣ Key URLs

| Service        | URL                                  |
| -------------- | ------------------------------------ |
| SearchFlow API | http://localhost:8007                |
| SearXNG Web    | http://localhost:8888                |
| API Docs       | http://localhost:8007/docs           |
| SearXNG Search | http://localhost:8888/search?q=query |

## 8️⃣ Environment Variables

Set in `.env`:

```bash
SEARXNG_URL=http://localhost:8888
SEARXNG_SECRET=your_secret_key
```

## Next Steps

1. ✅ Start SearXNG
2. ✅ Verify it's responding
3. ✅ Test in your code
4. ✅ Implement search endpoint
5. ✅ Add AI processing
6. ✅ Deploy

See `docs/11.SEARXNG_INTEGRATION.md` for complete guide.
