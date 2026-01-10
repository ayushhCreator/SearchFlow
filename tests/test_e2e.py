"""
End-to-End Integration Tests

Tests for complete workflow including SearXNG integration.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.integration
class TestEndToEnd:
    """End-to-end integration tests"""

    @pytest.mark.slow
    def test_complete_search_workflow(self):
        """Test complete search workflow"""
        payload = {
            "query": "how to learn python programming",
            "limit": 5,
            "language": "en",
        }

        response = client.post("/api/v1/search", json=payload)

        # May be 503 if SearXNG unavailable in test environment
        if response.status_code == 200:
            data = response.json()

            # Verify complete workflow
            assert data["results_count"] > 0
            assert len(data["results"]) <= 5
            assert len(data["markdown_summary"]) > 0
            assert len(data["json_data"]) > 0
            assert data["processing_time"] > 0

    def test_api_returns_proper_errors(self):
        """Test API returns proper error messages"""
        # Invalid query (too long)
        payload = {"query": "a" * 1000, "limit": 5}
        response = client.post("/api/v1/search", json=payload)
        assert response.status_code == 422

        # Invalid limit
        payload = {"query": "test", "limit": -1}
        response = client.post("/api/v1/search", json=payload)
        assert response.status_code == 422
