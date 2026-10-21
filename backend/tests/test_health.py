"""Automated tests for health check endpoints."""

from fastapi.testclient import TestClient

from app.core.config import settings


def test_root_health_endpoint(client: TestClient) -> None:
    """Test GET /health returns status 200 and expected health metadata."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
    assert data["environment"] == settings.ENVIRONMENT


def test_api_v1_health_endpoint(client: TestClient) -> None:
    """Test GET /api/v1/health returns status 200 and expected health metadata."""
    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
    assert data["environment"] == settings.ENVIRONMENT
