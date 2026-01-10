"""
Search API Tests

Tests for search endpoint functionality.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.unit
class TestSearchEndpoint:
    """Tests for search endpoint"""

    def test_search_endpoint_exists(self):
        """Test search endpoint is accessible"""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "search" in response.text.lower()

    def test_search_with_valid_query(self):
        """Test search with valid query"""
        payload = {"query": "FastAPI", "limit": 5, "language": "en"}
        response = client.post("/api/v1/search", json=payload)

        # Should either succeed or fail with proper error
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = response.json()
            assert "query" in data
            assert data["query"] == "FastAPI"
            assert "results_count" in data
            assert "markdown_summary" in data
            assert "json_data" in data

    def test_search_with_empty_query(self):
        """Test search rejects empty query"""
        payload = {"query": "", "limit": 5}
        response = client.post("/api/v1/search", json=payload)
        assert response.status_code == 422  # Validation error

    def test_search_with_limit_validation(self):
        """Test search validates limit parameter"""
        payload = {"query": "test", "limit": 100}  # Over max of 50
        response = client.post("/api/v1/search", json=payload)
        assert response.status_code == 422

    def test_search_response_structure(self):
        """Test search response has correct structure"""
        payload = {"query": "python", "limit": 3}
        response = client.post("/api/v1/search", json=payload)

        if response.status_code == 200:
            data = response.json()

            # Check required fields
            required_fields = [
                "query",
                "results_count",
                "results",
                "markdown_summary",
                "json_data",
                "processing_time",
                "timestamp",
            ]
            for field in required_fields:
                assert field in data, f"Missing field: {field}"

            # Check types
            assert isinstance(data["query"], str)
            assert isinstance(data["results_count"], int)
            assert isinstance(data["results"], list)
            assert isinstance(data["markdown_summary"], str)
            assert isinstance(data["processing_time"], float)


@pytest.mark.unit
def test_search_health_endpoint():
    """Test search health endpoint"""
    response = client.get("/api/v1/search/health")

    # Health check may be degraded if SearXNG unavailable
    assert response.status_code in [200, 503]

    if response.status_code == 200:
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]
