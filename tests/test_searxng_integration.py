"""
SearXNG Integration Tests

Tests for SearXNG search functionality and API integration.
"""

import pytest

from app.core.config import settings
from app.search.searxng_client import SearXNGClient


@pytest.mark.asyncio
class TestSearXNGClient:
    """Tests for SearXNGClient"""

    async def test_searxng_search_basic(self):
        """Test basic SearXNG search"""
        client = SearXNGClient()

        try:
            results = await client.search("python programming")

            assert isinstance(results, list)
            assert len(results) > 0

            # Check result structure
            for result in results:
                assert "title" in result
                assert "url" in result
                assert "snippet" in result
                assert "source" in result

        finally:
            await client.close()

    async def test_searxng_search_with_limit(self):
        """Test SearXNG search with result limit"""
        client = SearXNGClient()

        try:
            results = await client.search("fastapi", limit=5)

            assert isinstance(results, list)
            assert len(results) <= 5

        finally:
            await client.close()

    async def test_searxng_search_different_language(self):
        """Test SearXNG search with different language"""
        client = SearXNGClient()

        try:
            # Note: Results may vary depending on SearXNG configuration
            results = await client.search("machine learning", language="en")

            assert isinstance(results, list)

        finally:
            await client.close()

    async def test_searxng_context_manager(self):
        """Test SearXNG client as context manager"""
        async with SearXNGClient() as client:
            results = await client.search("test query")
            assert isinstance(results, list)

    async def test_searxng_empty_query(self):
        """Test SearXNG with empty query"""
        client = SearXNGClient()

        try:
            results = await client.search("")

            # Should return empty or error gracefully
            assert isinstance(results, list)

        finally:
            await client.close()


@pytest.mark.asyncio
class TestSearXNGIntegration:
    """Integration tests with FastAPI"""

    async def test_search_endpoint_basic(self):
        """Test basic search API endpoint"""
        # Note: This assumes the endpoint exists
        # Uncomment when API endpoint is implemented
        # from fastapi.testclient import TestClient
        # from app.main import app
        # client = TestClient(app)
        # response = client.post(
        #     "/api/v1/search",
        #     json={"query": "python"}
        # )
        #
        # assert response.status_code == 200
        # data = response.json()
        # assert "query" in data
        # assert "results" in data
        pass

    async def test_searxng_url_configuration(self):
        """Test SearXNG URL configuration"""
        assert settings.SEARXNG_URL is not None
        assert "localhost" in settings.SEARXNG_URL or "searxng" in settings.SEARXNG_URL
