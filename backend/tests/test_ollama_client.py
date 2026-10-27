"""Unit tests for the Ollama client with deterministic HTTP mocks."""

import httpx
import pytest

from app.llm.exceptions import (
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaResponseError,
    OllamaTimeoutError,
)
from app.llm.ollama_client import OllamaClient


def test_ollama_generate_success(monkeypatch):
    """Test successful generation response from Ollama API."""
    def mock_post(url, json=None, timeout=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            status_code=200,
            json={"message": {"content": "This is a grounded answer citing [Source: doc.pdf, Page 1]."}},
            request=request,
        )

    client = OllamaClient(base_url="http://mock-ollama:11434", model="test-model")
    monkeypatch.setattr(client.http_client, "post", mock_post)

    messages = [{"role": "user", "content": "Question"}]
    answer = client.generate(messages)

    assert "grounded answer" in answer
    assert "[Source: doc.pdf, Page 1]" in answer


def test_ollama_connection_error(monkeypatch):
    """Test handling when Ollama daemon is unreachable."""
    def mock_post(url, json=None, timeout=None):
        raise httpx.ConnectError("Connection refused")

    client = OllamaClient(base_url="http://mock-ollama:11434")
    monkeypatch.setattr(client.http_client, "post", mock_post)

    with pytest.raises(OllamaConnectionError, match="unreachable"):
        client.generate([{"role": "user", "content": "Hi"}])


def test_ollama_timeout_error(monkeypatch):
    """Test handling when Ollama generation times out."""
    def mock_post(url, json=None, timeout=None):
        raise httpx.TimeoutException("Read timed out")

    client = OllamaClient(base_url="http://mock-ollama:11434")
    monkeypatch.setattr(client.http_client, "post", mock_post)

    with pytest.raises(OllamaTimeoutError, match="timed out"):
        client.generate([{"role": "user", "content": "Hi"}])


def test_ollama_model_not_found(monkeypatch):
    """Test handling when configured model is not found in Ollama."""
    def mock_post(url, json=None, timeout=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            status_code=404,
            json={"error": "model 'nonexistent-model' not found, try pulling it first"},
            request=request,
        )

    client = OllamaClient(base_url="http://mock-ollama:11434", model="nonexistent-model")
    monkeypatch.setattr(client.http_client, "post", mock_post)

    with pytest.raises(OllamaModelNotFoundError, match="not found"):
        client.generate([{"role": "user", "content": "Hi"}])


def test_ollama_malformed_response(monkeypatch):
    """Test handling when Ollama returns non-200 or unexpected payload."""
    def mock_post(url, json=None, timeout=None):
        request = httpx.Request("POST", url)
        return httpx.Response(
            status_code=500,
            json={"error": "internal error in runner"},
            request=request,
        )

    client = OllamaClient(base_url="http://mock-ollama:11434")
    monkeypatch.setattr(client.http_client, "post", mock_post)

    with pytest.raises(OllamaResponseError, match="failed with status 500"):
        client.generate([{"role": "user", "content": "Hi"}])
