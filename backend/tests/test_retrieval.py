"""Unit and integration tests for embeddings and ChromaDB vector store."""

import hashlib
import pytest
import chromadb

from app.schemas.documents import DocumentChunk
from app.retrieval.embeddings import EmbeddingService
from app.retrieval.vector_store import VectorStore
from app.retrieval.exceptions import EmbeddingError, VectorStoreError


def deterministic_mock_embedder(texts: list[str]) -> list[list[float]]:
    """Generates a deterministic 384-dimensional vector from text for test isolation."""
    results = []
    for text in texts:
        # Use md5 hash to generate 384 deterministic pseudo-floats
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Create a 384-length vector
        vector = [(b / 255.0) for b in (h * 12)[:384]]
        results.append(vector)
    return results


@pytest.fixture
def mock_embedding_service() -> EmbeddingService:
    """Fixture providing an EmbeddingService backed by deterministic mock embedder."""
    return EmbeddingService(embedding_fn=deterministic_mock_embedder)


@pytest.fixture
def in_memory_vector_store(mock_embedding_service: EmbeddingService) -> VectorStore:
    """Fixture providing an in-memory ChromaDB VectorStore with an isolated collection per test."""
    import uuid
    client = chromadb.EphemeralClient()
    return VectorStore(
        client=client,
        collection_name=f"test_coll_{uuid.uuid4().hex}",
        embedding_service=mock_embedding_service,
    )


def test_embedding_generation_and_dimensions(mock_embedding_service: EmbeddingService):
    """Test generating embeddings for single queries and batches with correct dimensions."""
    query = "semantic search test query"
    query_vec = mock_embedding_service.embed_query(query)
    assert len(query_vec) == 384
    assert isinstance(query_vec[0], float)

    batch_texts = ["Sentence 1", "Sentence 2", "Sentence 3"]
    batch_vecs = mock_embedding_service.embed_texts(batch_texts)
    assert len(batch_vecs) == 3
    for vec in batch_vecs:
        assert len(vec) == 384


def test_embedding_empty_input_validation(mock_embedding_service: EmbeddingService):
    """Test that empty queries and empty lists are rejected with appropriate errors."""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        mock_embedding_service.embed_query("")

    with pytest.raises(ValueError, match="Query cannot be empty"):
        mock_embedding_service.embed_query("   \n\t  ")

    with pytest.raises(ValueError, match="Texts list cannot be empty"):
        mock_embedding_service.embed_texts([])


def test_vector_insertion_and_retrieval(in_memory_vector_store: VectorStore):
    """Test adding document chunks to vector store and retrieving by search query."""
    doc_id = "doc-123"
    chunks = [
        DocumentChunk(
            chunk_index=0,
            text="Machine learning enables semantic retrieval using embeddings.",
            page_number=1,
            source_filename="ai_paper.pdf",
            metadata={"char_start": 0, "char_end": 60},
        ),
        DocumentChunk(
            chunk_index=1,
            text="Relational databases like PostgreSQL store structured transaction records.",
            page_number=2,
            source_filename="ai_paper.pdf",
            metadata={"char_start": 61, "char_end": 135},
        ),
    ]

    added_count = in_memory_vector_store.add_chunks(document_id=doc_id, chunks=chunks)
    assert added_count == 2
    assert in_memory_vector_store.count() == 2

    # Query for exact match on machine learning
    results = in_memory_vector_store.search(
        query="Machine learning enables semantic retrieval using embeddings.",
        top_k=2,
    )
    assert len(results) == 2
    top_result = results[0]
    assert top_result.document_id == doc_id
    assert top_result.source_filename == "ai_paper.pdf"
    assert top_result.page_number == 1
    assert top_result.chunk_index == 0
    assert "Machine learning" in top_result.text
    # Distance should be 0.0 (or near 0) for exact match
    assert top_result.distance < 1e-4


def test_unique_ids_across_different_documents(in_memory_vector_store: VectorStore):
    """Test that chunk index 0 from doc A does not overwrite chunk index 0 from doc B."""
    doc_a = "doc-aaa"
    doc_b = "doc-bbb"

    chunk_a = DocumentChunk(
        chunk_index=0,
        text="Content of Document A",
        page_number=1,
        source_filename="doc_a.pdf",
    )
    chunk_b = DocumentChunk(
        chunk_index=0,
        text="Content of Document B",
        page_number=1,
        source_filename="doc_b.pdf",
    )

    in_memory_vector_store.add_chunks(doc_a, [chunk_a])
    in_memory_vector_store.add_chunks(doc_b, [chunk_b])

    assert in_memory_vector_store.count() == 2
    assert in_memory_vector_store.count_document(doc_a) == 1
    assert in_memory_vector_store.count_document(doc_b) == 1


def test_delete_document_isolation(in_memory_vector_store: VectorStore):
    """Test deleting one document does not affect another document's chunks."""
    doc_1 = "doc-to-delete"
    doc_2 = "doc-to-keep"

    in_memory_vector_store.add_chunks(
        doc_1,
        [
            DocumentChunk(chunk_index=0, text="Doc 1 Chunk 0", page_number=1, source_filename="d1.pdf"),
            DocumentChunk(chunk_index=1, text="Doc 1 Chunk 1", page_number=1, source_filename="d1.pdf"),
        ],
    )
    in_memory_vector_store.add_chunks(
        doc_2,
        [
            DocumentChunk(chunk_index=0, text="Doc 2 Chunk 0", page_number=1, source_filename="d2.pdf"),
        ],
    )

    assert in_memory_vector_store.count() == 3

    deleted_count = in_memory_vector_store.delete_document(doc_1)
    assert deleted_count == 2
    assert in_memory_vector_store.count() == 1
    assert in_memory_vector_store.count_document(doc_1) == 0
    assert in_memory_vector_store.count_document(doc_2) == 1


def test_search_empty_collection(in_memory_vector_store: VectorStore):
    """Test searching an empty collection returns empty list gracefully."""
    results = in_memory_vector_store.search("Any query", top_k=5)
    assert results == []


def test_search_invalid_parameters(in_memory_vector_store: VectorStore):
    """Test that empty queries and invalid top_k raise ValueError."""
    with pytest.raises(ValueError, match="Query cannot be empty"):
        in_memory_vector_store.search("", top_k=5)

    with pytest.raises(ValueError, match="top_k must be positive"):
        in_memory_vector_store.search("Valid query", top_k=0)

    with pytest.raises(ValueError, match="top_k must be positive"):
        in_memory_vector_store.search("Valid query", top_k=-2)


def test_search_document_filter(in_memory_vector_store: VectorStore):
    """Test searching filtered by specific document_id."""
    doc_target = "target-doc"
    doc_other = "other-doc"

    in_memory_vector_store.add_chunks(
        doc_target,
        [DocumentChunk(chunk_index=0, text="Specific target information", page_number=1, source_filename="target.pdf")],
    )
    in_memory_vector_store.add_chunks(
        doc_other,
        [DocumentChunk(chunk_index=0, text="Unrelated text in other doc", page_number=1, source_filename="other.pdf")],
    )

    results = in_memory_vector_store.search(
        query="Specific target information",
        top_k=5,
        document_id=doc_target,
    )
    assert len(results) == 1
    assert results[0].document_id == doc_target
