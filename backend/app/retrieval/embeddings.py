"""Modular embedding service using Sentence Transformers."""

import logging
from typing import Callable, Optional
from app.core.config import settings
from app.retrieval.exceptions import EmbeddingError

logger = logging.getLogger(__name__)

# Module-level model cache to prevent redundant re-instantiation
_MODEL_CACHE: dict[str, object] = {}


class EmbeddingService:
    """Service to generate dense vector embeddings from text using Sentence Transformers."""

    def __init__(
        self,
        model_name: Optional[str] = None,
        embedding_fn: Optional[Callable[[list[str]], list[list[float]]]] = None,
    ) -> None:
        self.model_name = model_name or settings.EMBEDDING_MODEL_NAME
        self._embedding_fn = embedding_fn

    def get_model(self):
        """Lazy-load and cache the SentenceTransformer model."""
        global _MODEL_CACHE
        if self.model_name not in _MODEL_CACHE:
            try:
                from sentence_transformers import SentenceTransformer

                logger.info("Loading SentenceTransformer model: %s", self.model_name)
                _MODEL_CACHE[self.model_name] = SentenceTransformer(self.model_name)
            except Exception as e:
                logger.error("Failed to load embedding model '%s': %s", self.model_name, str(e))
                raise EmbeddingError(f"Failed to load embedding model '{self.model_name}': {e}") from e
        return _MODEL_CACHE[self.model_name]

    def embed_texts(self, texts: list[str], batch_size: int = 32) -> list[list[float]]:
        """Generate embeddings for a list of text strings in batches.

        Args:
            texts: List of strings to embed.
            batch_size: Number of texts to process per batch.

        Returns:
            List of float vector embeddings.
        """
        if not texts:
            raise ValueError("Texts list cannot be empty.")

        # Clean strings
        cleaned = [t.strip() for t in texts]
        if not any(cleaned):
            raise ValueError("Texts list cannot contain only empty strings.")

        if self._embedding_fn is not None:
            return self._embedding_fn(cleaned)

        try:
            model = self.get_model()
            embeddings = model.encode(
                cleaned,
                batch_size=batch_size,
                show_progress_bar=False,
                normalize_embeddings=True,
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error("Error generating text embeddings: %s", str(e))
            raise EmbeddingError(f"Failed to generate text embeddings: {e}") from e

    def embed_query(self, query: str) -> list[float]:
        """Generate embedding vector for a single search query.

        Args:
            query: Search query text.

        Returns:
            A single float vector embedding.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        vectors = self.embed_texts([query.strip()])
        return vectors[0]
