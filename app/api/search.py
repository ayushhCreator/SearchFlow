"""
Search API Routes

REST and SSE endpoints for search functionality.
Uses SearchService for business logic (DRY/SOLID compliant).
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.cache.redis_client import get_cache_client
from app.services.search_service import get_search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


class SearchRequest(BaseModel):
    """Search request model"""

    query: str
    include_context: bool = True
    skip_cache: bool = False


class SearchResult(BaseModel):
    """Search result model"""

    question: str
    answer: str
    confidence: float
    sources: List[str]
    context: Optional[List[dict]] = None
    cached: bool = False


@router.post("/search", response_model=SearchResult)
async def search(request: SearchRequest) -> SearchResult:
    """
    Search and answer using DSPy + SearXNG

    Features:
    - Caching: Repeated queries return cached results instantly
    - AI Reasoning: DSPy synthesizes answers from web sources

    Example:
    ```bash
    curl -X POST http://localhost:8007/api/v1/search \\
      -H "Content-Type: application/json" \\
      -d '{"query": "what is dspy"}'
    ```
    """
    try:
        service = await get_search_service()
        result = await service.search(
            query=request.query,
            skip_cache=request.skip_cache,
            include_context=request.include_context,
        )

        return SearchResult(**result)

    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Search service not configured. Please set API keys in .env file.",
        )
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/stream")
async def search_stream(request: Request) -> EventSourceResponse:
    """
    Streaming search endpoint using Server-Sent Events (SSE).

    Streams:
    1. Status updates (searching, found sources, etc.)
    2. Answer tokens as they're generated
    3. Final sources

    Example:
    ```bash
    curl -N -X POST http://localhost:8007/api/v1/search/stream \\
      -H "Content-Type: application/json" \\
      -d '{"query": "what is python"}'
    ```
    """

    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            body = await request.json()
            query = body.get("query", "")
            skip_cache = body.get("skip_cache", False)

            if not query:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": "Query is required"}),
                }
                return

            logger.info(f"Streaming search: {query}")
            service = await get_search_service()

            async for event in service.search_streaming(query, skip_cache):
                event_type = event.get("type", "status")

                if event_type == "token":
                    yield {
                        "event": "token",
                        "data": json.dumps({"content": event.get("content", "")}),
                    }
                elif event_type == "status":
                    yield {
                        "event": "status",
                        "data": json.dumps({"message": event.get("message", "")}),
                    }
                elif event_type == "done":
                    yield {
                        "event": "done",
                        "data": json.dumps(
                            {
                                "sources": event.get("sources", []),
                                "confidence": event.get("confidence", 0),
                                "cached": event.get("cached", False),
                            }
                        ),
                    }
                elif event_type == "error":
                    yield {
                        "event": "error",
                        "data": json.dumps({"message": event.get("message", "")}),
                    }

                # Small delay for visual effect on status events
                if event_type == "status":
                    await asyncio.sleep(0.1)

        except Exception as e:
            logger.error(f"Streaming search failed: {e}")
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

    return EventSourceResponse(event_generator())


@router.get("/search/health")
async def search_health():
    """Health check for search functionality"""
    cache = await get_cache_client()
    cache_stats = await cache.get_stats()
    return {
        "status": "healthy",
        "searxng": "configured",
        "dspy": "ready",
        "cache": cache_stats,
    }


@router.delete("/cache")
async def clear_cache():
    """Clear all cached search results"""
    cache = await get_cache_client()
    deleted = await cache.clear_all()
    return {"message": f"Cleared {deleted} cached entries"}


@router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics"""
    cache = await get_cache_client()
    return await cache.get_stats()
