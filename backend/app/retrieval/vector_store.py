"""ChromaDB vector store integration for semantic retrieval."""

import logging
from typing import Optional
import chromadb
from chromadb.api import ClientAPI

from app.core.config import settings
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.exceptions import VectorStoreError
from app.schemas.documents import DocumentChunk, SearchResult

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages document chunk indexing and semantic vector search in ChromaDB."""

    def __init__(
        self,
        client: Optional[ClientAPI] = None,
        collection_name: Optional[str] = None,
        embedding_service: Optional[EmbeddingService] = None,
    ) -> None:
        self.collection_name = collection_name or settings.CHROMA_COLLECTION_NAME
        self.embedding_service = embedding_service or EmbeddingService()

        if client is not None:
            self.client = client
        else:
            self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIRECTORY)

        try:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            logger.error("Failed to initialize ChromaDB collection '%s': %s", self.collection_name, str(e))
            raise VectorStoreError(f"Failed to access or create collection '{self.collection_name}': {e}") from e

    def add_chunks(self, document_id: str, chunks: list[DocumentChunk]) -> int:
        """Store document chunks, their embeddings, and metadata with stable IDs.

        Args:
            document_id: Unique identifier for the document.
            chunks: List of DocumentChunk objects to embed and store.

        Returns:
            Number of chunks successfully indexed.
        """
        if not chunks:
            return 0

        ids = [f"{document_id}_{chunk.chunk_index}" for chunk in chunks]
        texts = [chunk.text for chunk in chunks]

        # Generate embeddings
        try:
            embeddings = self.embedding_service.embed_texts(texts)
        except Exception as e:
            logger.error("Embedding generation failed for document '%s': %s", document_id, str(e))
            raise VectorStoreError(f"Embedding generation failed: {e}") from e

        metadatas = []
        for chunk in chunks:
            meta = {
                "document_id": document_id,
                "source_filename": chunk.source_filename,
                "page_number": int(chunk.page_number),
                "chunk_index": int(chunk.chunk_index),
            }
            if chunk.metadata:
                for k, v in chunk.metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        meta[k] = v
                    else:
                        meta[k] = str(v)
            metadatas.append(meta)

        try:
            self.collection.upsert(
                ids=ids,
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            return len(chunks)
        except Exception as e:
            logger.error("Vector store insertion failed for document '%s': %s", document_id, str(e))
            # Attempt rollback of any partially added IDs
            try:
                self.collection.delete(ids=ids)
            except Exception:
                pass
            raise VectorStoreError(f"Failed to index chunks into vector store: {e}") from e

    def delete_document(self, document_id: str) -> int:
        """Delete all chunks belonging to a document.

        Args:
            document_id: Document ID whose chunks will be removed.

        Returns:
            Count of deleted chunks.
        """
        try:
            results = self.collection.get(where={"document_id": document_id})
            ids_to_delete = results.get("ids", [])
            if ids_to_delete:
                self.collection.delete(ids=ids_to_delete)
            return len(ids_to_delete)
        except Exception as e:
            logger.error("Failed to delete document '%s': %s", document_id, str(e))
            raise VectorStoreError(f"Failed to delete document '{document_id}': {e}") from e

    def count(self) -> int:
        """Return total number of chunks currently stored in the collection."""
        return self.collection.count()

    def count_document(self, document_id: str) -> int:
        """Return number of chunks stored for a specific document."""
        results = self.collection.get(where={"document_id": document_id})
        return len(results.get("ids", []))

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> list[SearchResult]:
        """Perform semantic search for relevant chunks given a natural language query.

        Args:
            query: User's question or search query.
            top_k: Maximum number of chunks to retrieve.
            document_id: Optional document ID to filter search scope.

        Returns:
            List of SearchResult objects ordered by relevance distance.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")

        if top_k <= 0:
            raise ValueError(f"top_k must be positive, got {top_k}")

        if self.collection.count() == 0:
            return []

        query_vec = self.embedding_service.embed_query(query.strip())
        where = {"document_id": document_id} if document_id else None

        n_results = min(top_k, self.collection.count())
        try:
            results = self.collection.query(
                query_embeddings=[query_vec],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            logger.error("Query execution failed in vector store: %s", str(e))
            raise VectorStoreError(f"Semantic search query failed: {e}") from e

        if not results or not results["documents"] or not results["documents"][0]:
            return []

        search_results: list[SearchResult] = []
        doc_list = results["documents"][0]
        meta_list = results["metadatas"][0]
        dist_list = results["distances"][0]

        for text, meta, dist in zip(doc_list, meta_list, dist_list):
            search_results.append(
                SearchResult(
                    text=text,
                    source_filename=str(meta.get("source_filename", "")),
                    page_number=int(meta.get("page_number", 1)),
                    chunk_index=int(meta.get("chunk_index", 0)),
                    document_id=str(meta.get("document_id", "")),
                    distance=float(dist),
                    metadata=meta,
                )
            )

        return search_results
