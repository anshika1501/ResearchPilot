"""Pydantic schemas for document ingestion and chunking."""

from typing import Any, Optional
import uuid
from pydantic import BaseModel, Field


class ExtractedPage(BaseModel):
    """Schema representing an individual page extracted from a document."""

    page_number: int = Field(..., description="1-based page number within the document", ge=1)
    text: str = Field(..., description="Extracted plain text content of the page")
    char_count: int = Field(..., description="Total character count of extracted text", ge=0)


class DocumentChunk(BaseModel):
    """Schema representing a deterministic chunk of text from a document."""

    chunk_index: int = Field(..., description="0-based sequential chunk index", ge=0)
    text: str = Field(..., description="Chunk text content")
    page_number: int = Field(..., description="1-based page number where the chunk originated", ge=1)
    source_filename: str = Field(..., description="Original filename of the document")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional chunk metadata (e.g. character offsets, total document pages)",
    )


class DocumentUploadResponse(BaseModel):
    """Schema for document upload API response."""

    document_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier assigned to the document in the vector store",
    )
    filename: str = Field(..., description="Original filename of the uploaded document")
    file_size_bytes: int = Field(..., description="Size of the uploaded file in bytes", ge=0)
    page_count: int = Field(..., description="Total number of pages in the document", ge=1)
    total_chunks: int = Field(..., description="Total number of text chunks generated", ge=0)
    pages: list[ExtractedPage] = Field(..., description="List of extracted pages with page numbers")
    chunks: list[DocumentChunk] = Field(..., description="List of generated text chunks")


class SearchRequest(BaseModel):
    """Schema for semantic retrieval search query."""

    query: str = Field(..., min_length=1, description="Natural language search query")
    top_k: int = Field(default=5, ge=1, le=50, description="Maximum number of chunks to retrieve")
    document_id: Optional[str] = Field(
        default=None,
        description="Optional filter to retrieve only chunks from a specific document",
    )


class SearchResult(BaseModel):
    """Schema for a single retrieved chunk with relevance distance and provenance."""

    text: str = Field(..., description="Content of the retrieved text chunk")
    source_filename: str = Field(..., description="Source filename of the document")
    page_number: int = Field(..., description="1-based page number of the source chunk", ge=1)
    chunk_index: int = Field(..., description="0-based chunk index within the document", ge=0)
    document_id: str = Field(..., description="Document identifier")
    distance: float = Field(
        ...,
        description="ChromaDB vector distance score (smaller means more similar; distance is not a probability)",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional chunk metadata")


class SearchResponse(BaseModel):
    """Schema for semantic retrieval search response."""

    query: str = Field(..., description="Original search query")
    results: list[SearchResult] = Field(..., description="List of retrieved chunks ordered by relevance")
    total_results: int = Field(..., description="Count of retrieved results", ge=0)

