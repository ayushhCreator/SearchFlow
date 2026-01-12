"""
MCP Search Tools

Defines the search tools exposed via MCP protocol.
AI agents can use these tools to search the web.
"""

import logging
from typing import Any, Dict, Optional

from app.ai.dspy_pipeline import DSPyPipeline
from app.cache.redis_client import CacheClient

logger = logging.getLogger(__name__)


class SearchTools:
    """
    Search tools for MCP server.

    Provides:
    - web_search: Quick search with AI-synthesized answer
    - research_topic: Deep research with follow-up queries
    - get_sources: Get raw sources without AI synthesis
    """

    def __init__(self, cache: Optional[CacheClient] = None):
        """
        Initialize search tools.

        Args:
            cache: Optional cache client for faster responses
        """
        self.cache = cache
        self._pipeline: Optional[DSPyPipeline] = None

    def _get_pipeline(self) -> DSPyPipeline:
        """Get or create DSPy pipeline."""
        if self._pipeline is None:
            self._pipeline = DSPyPipeline(k_results=5)
        return self._pipeline

    async def web_search(
        self,
        query: str,
        skip_cache: bool = False,
    ) -> Dict[str, Any]:
        """
        Search the web and get an AI-synthesized answer.

        Args:
            query: The search query or question
            skip_cache: If True, bypass cache and force fresh search

        Returns:
            Dict with answer, sources, and confidence score
        """
        logger.info(f"MCP web_search: {query}")

        # Check cache first
        if self.cache and not skip_cache:
            cached = await self.cache.get(query)
            if cached:
                logger.info("Returning cached result for MCP search")
                return {
                    "answer": cached.get("answer", ""),
                    "sources": cached.get("sources", []),
                    "confidence": cached.get("confidence", 0),
                    "cached": True,
                }

        # Perform search
        try:
            pipeline = self._get_pipeline()
            result = pipeline.search_and_answer(query)

            # Cache result
            if self.cache:
                await self.cache.set(query, result)

            return {
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0),
                "cached": False,
            }

        except Exception as e:
            logger.error(f"MCP web_search failed: {e}")
            return {
                "error": str(e),
                "answer": "",
                "sources": [],
                "confidence": 0,
            }

    async def research_topic(
        self,
        topic: str,
        depth: int = 3,
    ) -> Dict[str, Any]:
        """
        Deep research on a topic with multiple related queries.

        Args:
            topic: The topic to research
            depth: Number of related queries to explore (1-5)

        Returns:
            Dict with comprehensive research summary
        """
        logger.info(f"MCP research_topic: {topic} (depth={depth})")

        depth = max(1, min(5, depth))  # Clamp to 1-5

        # Generate related queries
        related_queries = [
            topic,
            f"what is {topic}",
            f"{topic} benefits",
            f"{topic} challenges",
            f"how does {topic} work",
        ][:depth]

        results = []
        all_sources = []

        for query in related_queries:
            result = await self.web_search(query)
            if not result.get("error"):
                results.append(
                    {
                        "query": query,
                        "answer": result.get("answer", ""),
                    }
                )
                all_sources.extend(result.get("sources", []))

        # Deduplicate sources
        unique_sources = list(set(all_sources))

        return {
            "topic": topic,
            "research": results,
            "sources": unique_sources[:10],  # Limit to 10 sources
            "queries_explored": len(results),
        }

    async def get_sources(
        self,
        query: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """
        Get raw sources without AI synthesis.

        Useful when you want to see the actual search results
        before AI processing.

        Args:
            query: The search query
            limit: Maximum number of sources to return

        Returns:
            Dict with list of sources
        """
        logger.info(f"MCP get_sources: {query}")

        try:
            pipeline = self._get_pipeline()

            # Access the retriever directly for raw results
            _passages = pipeline.retriever(query)  # noqa: F841
            raw_results = getattr(pipeline.retriever, "_last_results", [])

            sources = []
            for i, result in enumerate(raw_results[:limit]):
                sources.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", "")[:300],
                        "engine": result.get("engine", "unknown"),
                    }
                )

            return {
                "query": query,
                "sources": sources,
                "total_found": len(raw_results),
            }

        except Exception as e:
            logger.error(f"MCP get_sources failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "sources": [],
            }
