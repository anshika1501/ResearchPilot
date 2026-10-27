"""Custom exceptions for vector retrieval and embeddings."""


class RetrievalError(Exception):
    """Base exception for all retrieval and vector store errors."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class EmbeddingError(RetrievalError):
    """Raised when embedding model generation or loading fails."""


class VectorStoreError(RetrievalError):
    """Raised when vector database operations fail."""


class DocumentNotFoundError(RetrievalError):
    """Raised when a requested document ID does not exist in the vector store."""
