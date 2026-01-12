"""
Search API Routes

This module defines the search endpoints using DSPy + SearXNG.
Includes caching and streaming support.
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, List, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.ai.dspy_pipeline import DSPyPipeline
from app.cache.redis_client import get_cache_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["search"])


class SearchRequest(BaseModel):
    """Search request model"""

    query: str
    include_context: bool = True
    skip_cache: bool = False  # Force fresh search


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
        logger.info(f"Search request: {request.query}")

        # Check cache first (unless skip_cache is set)
        cache = await get_cache_client()
        if not request.skip_cache:
            cached_result = await cache.get(request.query)
            if cached_result:
                logger.info("Returning cached result")
                return SearchResult(
                    question=cached_result["question"],
                    answer=cached_result["answer"],
                    confidence=cached_result["confidence"],
                    sources=cached_result.get("sources", []),
                    context=cached_result.get("context")
                    if request.include_context
                    else None,
                    cached=True,
                )

        # Initialize DSPy pipeline
        try:
            pipeline = DSPyPipeline(k_results=5)
        except ValueError as e:
            logger.error(f"DSPy initialization failed: {e}")
            raise HTTPException(
                status_code=503,
                detail="Search service not configured. Please set API keys in .env file.",
            )

        # Search and answer
        result = pipeline.search_and_answer(request.query)

        # Store in cache
        await cache.set(request.query, result)

        # Format response
        response = SearchResult(
            question=result["question"],
            answer=result["answer"],
            confidence=result["confidence"],
            sources=result.get("sources", []),
            context=result.get("context") if request.include_context else None,
            cached=False,
        )

        return response

    except HTTPException:
        raise
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
            # Parse request body
            body = await request.json()
            query = body.get("query", "")
            skip_cache = body.get("skip_cache", False)

            if not query:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": "Query is required"}),
                }
                return

            logger.info(f"Streaming search request: {query}")

            # Check cache first
            cache = await get_cache_client()
            if not skip_cache:
                cached_result = await cache.get(query)
                if cached_result:
                    yield {
                        "event": "status",
                        "data": json.dumps({"message": "Found cached result"}),
                    }
                    await asyncio.sleep(0.1)

                    # Stream cached answer word by word for visual effect
                    answer = cached_result.get("answer", "")
                    words = answer.split()
                    for i, word in enumerate(words):
                        yield {
                            "event": "token",
                            "data": json.dumps({"content": word + " "}),
                        }
                        await asyncio.sleep(0.02)  # Small delay for visual effect

                    yield {
                        "event": "done",
                        "data": json.dumps(
                            {
                                "sources": cached_result.get("sources", []),
                                "confidence": cached_result.get("confidence", 0),
                                "cached": True,
                            }
                        ),
                    }
                    return

            # Status: Searching
            yield {
                "event": "status",
                "data": json.dumps({"message": "Searching the web..."}),
            }
            await asyncio.sleep(0.1)

            # Initialize DSPy pipeline
            try:
                pipeline = DSPyPipeline(k_results=5)
            except ValueError as e:
                yield {
                    "event": "error",
                    "data": json.dumps({"message": f"Configuration error: {str(e)}"}),
                }
                return

            # Status: Found sources
            yield {
                "event": "status",
                "data": json.dumps({"message": "Analyzing sources..."}),
            }
            await asyncio.sleep(0.1)

            # Perform search (this is blocking, but we stream the result)
            result = pipeline.search_and_answer(query)

            # Status: Reasoning
            yield {
                "event": "status",
                "data": json.dumps({"message": "Generating answer..."}),
            }
            await asyncio.sleep(0.1)

            # Stream answer word by word
            answer = result.get("answer", "")
            words = answer.split()
            for word in words:
                yield {"event": "token", "data": json.dumps({"content": word + " "})}
                await asyncio.sleep(0.03)  # Simulate token streaming

            # Cache the result
            await cache.set(query, result)

            # Done event with metadata
            yield {
                "event": "done",
                "data": json.dumps(
                    {
                        "sources": result.get("sources", []),
                        "confidence": result.get("confidence", 0),
                        "context": result.get("context", []),
                        "cached": False,
                    }
                ),
            }

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
