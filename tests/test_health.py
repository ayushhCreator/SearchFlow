"""
Health Check Tests

Tests for API health endpoints.
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns success"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "SearchFlow is running"


def test_health_endpoint():
    """Test health endpoint returns healthy status"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
