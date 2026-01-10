"""
SearXNG Search Engine Client

This module handles communication with SearXNG for live web search.
"""

import logging
from typing import Dict, List, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SearXNGClient:
    """Client for interacting with SearXNG search engine"""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize SearXNG client

        Args:
            base_url: SearXNG instance URL (defaults to settings)
        """
        self.base_url = base_url or settings.SEARXNG_URL
        self.client = httpx.AsyncClient(timeout=30.0)

    async def search(
        self, query: str, limit: int = 10, language: str = "en"
    ) -> List[Dict]:
        """
        Perform search query

        Args:
            query: Search query string
            limit: Maximum number of results
            language: Language code

        Returns:
            List of search results

        Raises:
            httpx.HTTPError: If search request fails
        """
        try:
            logger.info(f"Searching SearXNG for: {query}")

            # Prepare request
            params = {
                "q": query,
                "format": "json",
                "limit": limit,
                "language": language,
            }

            # Make request
            response = await self.client.get(f"{self.base_url}/search", params=params)
            response.raise_for_status()

            # Parse response
            data = response.json()
            results = []

            for result in data.get("results", []):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", ""),
                        "source": result.get("engine", "Unknown"),
                    }
                )

            logger.info(f"Found {len(results)} results")
            return results

        except httpx.HTTPError as e:
            logger.error(f"SearXNG request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing SearXNG response: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close()
