"""
DSPy-compatible SearXNG Retriever

Bridges DSPy and SearXNG for web search in AI pipelines.
"""

import logging
from typing import List, Optional

import dspy
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class SearXNGRetriever(dspy.Retrieve):
    """DSPy retriever that uses SearXNG for web search"""

    def __init__(
        self, searx_url: Optional[str] = None, k: int = 5, language: str = "en"
    ):
        """
        Initialize SearXNG retriever for DSPy

        Args:
            searx_url: SearXNG base URL (defaults to settings)
            k: Number of results to retrieve
            language: Language code for search
        """
        super().__init__(k=k)
        self.searx_url = searx_url or settings.SEARXNG_URL
        self.language = language
        self._last_results = []  # Store raw results with metadata

    def forward(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        Retrieve relevant passages from web via SearXNG

        Args:
            query: Search query string
            k: Number of results (overrides instance k)

        Returns:
            List of text passages with metadata
        """
        k = k or self.k

        try:
            logger.info(f"Retrieving from SearXNG: {query}")

            response = requests.get(
                f"{self.searx_url}/search",
                params={
                    "q": query,
                    "format": "json",
                    "language": self.language,
                    "safesearch": 1,
                },
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            # Store results with metadata for later use
            self._last_results = data.get("results", [])[:k]

            # Return passages as strings (DSPy expects List[str])
            passages = []
            for result in self._last_results:
                # Combine title and content for better context
                text = f"{result.get('title', '')}\n{result.get('content', '')}"
                passages.append(text.strip())

            logger.info(f"Retrieved {len(passages)} passages")
            return passages

        except Exception as e:
            logger.error(f"SearXNG retrieval failed: {e}")
            self._last_results = []
            return []
