"""
Search Service

Centralized business logic for search operations.
Single Responsibility: Only handles search operations.
"""

import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

from app.ai.pipeline import DSPyPipeline
from app.cache.redis_client import CacheClient, get_cache_client

logger = logging.getLogger(__name__)

_search_service: Optional["SearchService"] = None


class SearchService:
    """Centralized search service with caching and streaming."""

    def __init__(
        self,
        cache: Optional[CacheClient] = None,
        pipeline: Optional[DSPyPipeline] = None,
        k_results: int = 5,
    ):
        """Initialize search service."""
        self._cache = cache
        self._pipeline = pipeline
        self._k_results = k_results

    async def _get_cache(self) -> CacheClient:
        """Get cache client, initializing if needed."""
        if self._cache is None:
            self._cache = await get_cache_client()
        return self._cache

    def _get_pipeline(self) -> DSPyPipeline:
        """Get or create DSPy pipeline."""
        if self._pipeline is None:
            self._pipeline = DSPyPipeline(k_results=self._k_results)
        return self._pipeline

    async def search(
        self,
        query: str,
        skip_cache: bool = False,
        include_context: bool = True,
    ) -> Dict[str, Any]:
        """Perform a search with caching."""
        logger.info(f"SearchService.search: {query[:50]}...")

        cache = await self._get_cache()

        if not skip_cache:
            cached_result = await cache.get(query)
            if cached_result:
                logger.info("Returning cached result")
                return self._format_result(cached_result, True, include_context)

        try:
            pipeline = self._get_pipeline()
            result = pipeline.search_and_answer(query)
            await cache.set(query, result)
            return self._format_result(result, False, include_context)

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def _format_result(
        self,
        result: Dict[str, Any],
        cached: bool,
        include_context: bool,
    ) -> Dict[str, Any]:
        """Format search result consistently."""
        return {
            "question": result.get("question", ""),
            "answer": result.get("answer", ""),
            "confidence": result.get("confidence", 0.0),
            "sources": result.get("sources", []),
            "context": result.get("context") if include_context else None,
            "cached": cached,
        }

    async def search_streaming(
        self,
        query: str,
        skip_cache: bool = False,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Perform a streaming search."""
        cache = await self._get_cache()

        if not skip_cache:
            cached_result = await cache.get(query)
            if cached_result:
                yield {"type": "status", "message": "Found cached result"}
                async for event in self._stream_words(cached_result.get("answer", "")):
                    yield event
                yield {
                    "type": "done",
                    "sources": cached_result.get("sources", []),
                    "confidence": cached_result.get("confidence", 0),
                    "cached": True,
                }
                return

        yield {"type": "status", "message": "Searching the web..."}

        try:
            pipeline = self._get_pipeline()
        except ValueError as e:
            yield {"type": "error", "message": f"Configuration error: {str(e)}"}
            return

        yield {"type": "status", "message": "Analyzing sources..."}
        result = pipeline.search_and_answer(query)

        yield {"type": "status", "message": "Generating answer..."}
        async for event in self._stream_words(result.get("answer", "")):
            yield event

        await cache.set(query, result)

        yield {
            "type": "done",
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0),
            "context": result.get("context", []),
            "cached": False,
        }

    async def _stream_words(
        self,
        text: str,
        delay: float = 0.03,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream text word by word."""
        for word in text.split():
            yield {"type": "token", "content": word + " "}
            await asyncio.sleep(delay)

    async def get_sources(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Get raw sources without AI synthesis."""
        logger.info(f"SearchService.get_sources: {query[:50]}...")
        try:
            pipeline = self._get_pipeline()
            _ = pipeline.retriever(query)
            raw_results = getattr(pipeline.retriever, "_last_results", [])

            sources = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", "")[:300],
                    "engine": r.get("engine", "unknown"),
                }
                for r in raw_results[:limit]
            ]

            return {"query": query, "sources": sources, "total_found": len(raw_results)}
        except Exception as e:
            logger.error(f"get_sources failed: {e}")
            return {"error": str(e), "query": query, "sources": []}

    async def research_topic(self, topic: str, depth: int = 3) -> Dict[str, Any]:
        """Deep research on a topic."""
        logger.info(f"SearchService.research_topic: {topic} (depth={depth})")
        depth = max(1, min(5, depth))

        related_queries = [
            topic,
            f"what is {topic}",
            f"{topic} benefits",
            f"{topic} challenges",
            f"how does {topic} work",
        ][:depth]

        results: List[Dict[str, Any]] = []
        all_sources: List[str] = []

        for query in related_queries:
            result = await self.search(query)
            if "error" not in result:
                results.append({"query": query, "answer": result.get("answer", "")})
                all_sources.extend(result.get("sources", []))

        return {
            "topic": topic,
            "research": results,
            "sources": list(set(all_sources))[:10],
            "queries_explored": len(results),
        }


async def get_search_service() -> SearchService:
    """Get or create global search service."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service
