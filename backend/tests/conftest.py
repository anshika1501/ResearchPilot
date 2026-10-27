"""Pytest fixtures and configuration."""

from collections.abc import Generator
import hashlib
import uuid
import pytest
import chromadb
from fastapi.testclient import TestClient

from app.api.deps import get_vector_store
from app.main import app
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore


def _test_embedder(texts: list[str]) -> list[list[float]]:
    """Deterministic 384-dimensional test embedding function."""
    res = []
    for t in texts:
        h = hashlib.sha256(t.encode("utf-8")).digest()
        res.append([(b / 255.0) for b in (h * 12)[:384]])
    return res


@pytest.fixture
def mock_vector_store() -> VectorStore:
    """Isolated in-memory VectorStore for tests."""
    client = chromadb.EphemeralClient()
    service = EmbeddingService(embedding_fn=_test_embedder)
    return VectorStore(
        client=client,
        collection_name=f"test_{uuid.uuid4().hex}",
        embedding_service=service,
    )


@pytest.fixture
def client(mock_vector_store: VectorStore) -> Generator[TestClient, None, None]:
    """Test client fixture configured with an isolated in-memory vector store."""
    app.dependency_overrides[get_vector_store] = lambda: mock_vector_store
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

