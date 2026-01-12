"""
MCP Search Tools

Defines the search tools exposed via MCP protocol.
AI agents can use these tools to search the web.

Uses SearchService for business logic (DRY/SOLID compliant).
"""

import logging
from typing import Any, Dict, Optional

from app.cache.redis_client import CacheClient
from app.services import SearchService

logger = logging.getLogger(__name__)


class SearchTools:
    """
    Search tools for MCP server.

    Thin wrapper around SearchService that formats results
    for AI agent consumption.

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
        # Use composition - delegate to SearchService
        self._service = SearchService(cache=cache)

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

        try:
            result = await self._service.search(
                query=query,
                skip_cache=skip_cache,
                include_context=False,  # MCP doesn't need full context
            )

            return {
                "answer": result.get("answer", ""),
                "sources": result.get("sources", []),
                "confidence": result.get("confidence", 0),
                "cached": result.get("cached", False),
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

        try:
            return await self._service.research_topic(topic, depth)
        except Exception as e:
            logger.error(f"MCP research_topic failed: {e}")
            return {
                "error": str(e),
                "topic": topic,
                "research": [],
                "sources": [],
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
            return await self._service.get_sources(query, limit)
        except Exception as e:
            logger.error(f"MCP get_sources failed: {e}")
            return {
                "error": str(e),
                "query": query,
                "sources": [],
            }
