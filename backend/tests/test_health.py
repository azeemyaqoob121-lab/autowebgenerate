"""
Health Endpoint Tests

Tests for API health check and information endpoints.
These endpoints don't require authentication.
"""
import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_root_endpoint(client: TestClient):
    """Test root endpoint returns API information."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data
    assert "version" in data
    assert "environment" in data
    assert "docs" in data
    assert "health" in data

    assert data["docs"] == "/docs"
    assert data["health"] == "/api/health"


@pytest.mark.integration
def test_health_check_endpoint(client: TestClient):
    """Test health check endpoint returns system status."""
    response = client.get("/api/health")

    assert response.status_code == 200
    data = response.json()

    # Verify all required fields are present
    assert "status" in data
    assert "version" in data
    assert "environment" in data
    assert "timestamp" in data
    assert "database" in data

    # Verify field values
    assert data["status"] == "healthy"
    assert data["database"] in ["connected", "unavailable"]

    # Verify timestamp is ISO format
    assert "T" in data["timestamp"]
    assert "Z" in data["timestamp"]


@pytest.mark.integration
def test_health_check_response_headers(client: TestClient):
    """Test health check response includes required headers."""
    response = client.get("/api/health")

    assert response.status_code == 200

    # Check for request tracking headers
    assert "X-Request-ID" in response.headers or "x-request-id" in response.headers
    assert "X-Process-Time" in response.headers or "x-process-time" in response.headers


@pytest.mark.integration
def test_health_check_performance(client: TestClient):
    """Test health check responds quickly (< 1 second)."""
    import time

    start_time = time.time()
    response = client.get("/api/health")
    end_time = time.time()

    duration = end_time - start_time

    assert response.status_code == 200
    assert duration < 1.0, f"Health check took {duration:.2f}s, should be < 1s"


@pytest.mark.integration
def test_multiple_health_checks(client: TestClient):
    """Test multiple health checks return consistent results."""
    responses = [client.get("/api/health") for _ in range(5)]

    assert all(r.status_code == 200 for r in responses)

    statuses = [r.json()["status"] for r in responses]
    assert all(status == "healthy" for status in statuses)

    db_statuses = [r.json()["database"] for r in responses]
    # All should have same database status
    assert len(set(db_statuses)) == 1
