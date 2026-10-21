"""Pytest fixtures and configuration."""

from collections.abc import Generator
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """Test client fixture configured for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client
