"""FastAPI dependencies for dependency injection."""

from functools import lru_cache
from fastapi import Depends
from app.llm.ollama_client import OllamaClient
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore
from app.services.rag_service import RAGService


@lru_cache
def get_embedding_service() -> EmbeddingService:
    """Dependency provider for EmbeddingService singleton."""
    return EmbeddingService()


def get_vector_store() -> VectorStore:
    """Dependency provider for ChromaDB VectorStore."""
    return VectorStore(embedding_service=get_embedding_service())


def get_ollama_client() -> OllamaClient:
    """Dependency provider for OllamaClient."""
    return OllamaClient()


def get_rag_service(
    vector_store: VectorStore = Depends(get_vector_store),
    ollama_client: OllamaClient = Depends(get_ollama_client),
) -> RAGService:
    """Dependency provider for RAGService."""
    return RAGService(vector_store=vector_store, llm_client=ollama_client)

