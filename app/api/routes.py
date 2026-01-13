"""
API Routes

REST and SSE endpoints for search functionality.
Uses SearchService for business logic (DRY/SOLID compliant).
"""

import asyncio
import json
import logging
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from sse_starlette.sse import EventSourceResponse

from app.api.models import SearchRequest, SearchResult
from app.cache.redis_client import get_cache_client
from app.services import get_search_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


@router.post("/search", response_model=SearchResult)
async def search(request: SearchRequest) -> SearchResult:
    """Search and answer using DSPy + SearXNG."""
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
        raise HTTPException(status_code=503, detail="Search service not configured.")
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search/stream")
async def search_stream(request: Request) -> EventSourceResponse:
    """Streaming search endpoint using SSE."""

    async def event_generator() -> AsyncGenerator[dict, None]:
        try:
            body = await request.json()
            query = body.get("query", "")
            skip_cache = body.get("skip_cache", False)
            # Model is controlled by .env, not frontend

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
                    await asyncio.sleep(0.1)
                elif event_type == "done":
                    yield {
                        "event": "done",
                        "data": json.dumps(
                            {
                                "sources": event.get("sources", []),
                                "context": event.get("context", []),
                                "confidence": event.get("confidence", 0),
                                "cached": event.get("cached", False),
                                "model_used": event.get("model_used", "unknown"),
                            }
                        ),
                    }
                elif event_type == "error":
                    yield {
                        "event": "error",
                        "data": json.dumps({"message": event.get("message", "")}),
                    }

        except Exception as e:
            logger.error(f"Streaming search failed: {e}")
            yield {"event": "error", "data": json.dumps({"message": str(e)})}

    return EventSourceResponse(event_generator())


@router.get("/search/health")
async def search_health():
    """Health check for search functionality."""
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
    """Clear all cached search results."""
    cache = await get_cache_client()
    deleted = await cache.clear_all()
    return {"message": f"Cleared {deleted} cached entries"}


@router.get("/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    cache = await get_cache_client()
    return await cache.get_stats()


@router.post("/suggestions")
async def get_suggestions(request: Request):
    """Get AI-powered search suggestions.

    For new users: Returns suggestions based on trending tech topics.
    For returning users: Returns personalized suggestions based on history.
    """
    try:
        from app.services.suggestions import get_suggestion_service

        body = await request.json()
        history = body.get("history", [])

        service = get_suggestion_service()
        suggestions = await service.generate_suggestions_async(history)

        return {
            "suggestions": suggestions,
            "personalized": len(history) > 0,
        }

    except Exception as e:
        logger.error(f"Suggestions failed: {e}")
        # Return fallback suggestions on error
        return {
            "suggestions": [
                "What are the latest features in Next.js?",
                "Explain quantum computing simply",
                "Best practices for React performance",
                "How does a transformer model work?",
                "Compare Python vs Rust for backend",
            ],
            "personalized": False,
            "error": str(e),
        }
