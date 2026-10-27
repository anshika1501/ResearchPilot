"""Vector retrieval module: embeddings, vector store integration, and retrievers."""

from app.retrieval.embeddings import EmbeddingService
from app.retrieval.exceptions import (
    DocumentNotFoundError,
    EmbeddingError,
    RetrievalError,
    VectorStoreError,
)
from app.retrieval.vector_store import VectorStore

__all__ = [
    "EmbeddingService",
    "VectorStore",
    "RetrievalError",
    "EmbeddingError",
    "VectorStoreError",
    "DocumentNotFoundError",
]

