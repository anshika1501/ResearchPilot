"""Pydantic schemas for RAG chat and grounded question answering."""

from typing import Optional
from pydantic import BaseModel, Field

from app.core.config import settings


class Citation(BaseModel):
    """Schema for an individual source citation supporting a claim."""

    source_filename: str = Field(..., description="Name of the source document file")
    page_number: int = Field(..., description="1-based page number where the claim is supported", ge=1)
    document_id: str = Field(..., description="ID of the document")
    chunk_index: int = Field(..., description="Chunk index within the document", ge=0)


class EvidencePassage(BaseModel):
    """Schema for a retrieved context passage supplied as evidence."""

    text: str = Field(..., description="Extracted text excerpt")
    source_filename: str = Field(..., description="Source document filename")
    page_number: int = Field(..., description="1-based page number", ge=1)
    document_id: str = Field(..., description="Document identifier")
    chunk_index: int = Field(..., description="Chunk index", ge=0)
    distance: float = Field(..., description="Vector distance score from semantic search")


class ChatRequest(BaseModel):
    """Request payload for RAG question answering."""

    question: str = Field(
        ...,
        min_length=1,
        max_length=settings.MAX_QUESTION_LENGTH,
        description="Natural language question to ask about uploaded documents",
    )
    document_id: Optional[str] = Field(
        default=None,
        description="Optional filter to scope answer generation to a specific document",
    )
    top_k: int = Field(
        default=settings.DEFAULT_TOP_K,
        ge=1,
        le=20,
        description="Number of relevant document chunks to retrieve as context",
    )


class ChatResponse(BaseModel):
    """Response payload for grounded RAG answer with citations and evidence."""

    question: str = Field(..., description="Original user question")
    answer: str = Field(..., description="Grounded answer generated from evidence")
    citations: list[Citation] = Field(default_factory=list, description="List of source citations")
    evidence: list[EvidencePassage] = Field(
        default_factory=list,
        description="Retrieved source excerpts supplied as evidence to the model",
    )
    has_sufficient_evidence: bool = Field(
        ...,
        description="Whether sufficient relevant evidence was found to answer the question",
    )
    model: str = Field(..., description="Model identifier used for answer generation")
