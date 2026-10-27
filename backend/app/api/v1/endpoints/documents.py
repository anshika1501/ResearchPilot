"""Document management, upload, and semantic search endpoints."""

import logging
import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from app.api.deps import get_vector_store
from app.core.config import settings
from app.ingestion.chunker import TextChunker
from app.ingestion.exceptions import (
    EmptyPDFError,
    EncryptedPDFError,
    FileSizeExceededError,
    IngestionError,
    InvalidPDFError,
    NoExtractableTextError,
)
from app.ingestion.pdf_parser import PDFParser
from app.retrieval.exceptions import VectorStoreError
from app.retrieval.vector_store import VectorStore
from app.schemas.documents import (
    DocumentUploadResponse,
    SearchRequest,
    SearchResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload and ingest a PDF document",
    description="Upload a PDF document to extract page-aware text, split it into deterministic chunks, and index into ChromaDB.",
)
async def upload_document(
    file: UploadFile = File(..., description="PDF document file to upload"),
    vector_store: VectorStore = Depends(get_vector_store),
) -> DocumentUploadResponse:
    """Upload and parse a PDF document, extracting text page-by-page, chunking it, and indexing in ChromaDB."""
    filename = file.filename or "unknown.pdf"

    # Validate file extension
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type for '{filename}'. Only PDF files are supported.",
        )

    try:
        content = await file.read()
    except Exception as e:
        logger.error("Failed to read upload stream for '%s': %s", filename, str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file '{filename}'.",
        ) from e

    parser = PDFParser(max_file_size=settings.MAX_UPLOAD_SIZE_BYTES)
    chunker = TextChunker(
        chunk_size=settings.DEFAULT_CHUNK_SIZE,
        chunk_overlap=settings.DEFAULT_CHUNK_OVERLAP,
    )

    try:
        extracted_pages = parser.extract_text(pdf_bytes=content, filename=filename)
        chunks = chunker.chunk_pages(pages=extracted_pages, source_filename=filename)
    except FileSizeExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=e.message,
        ) from e
    except NoExtractableTextError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=e.message,
        ) from e
    except (EmptyPDFError, InvalidPDFError, EncryptedPDFError, IngestionError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        ) from e

    document_id = str(uuid.uuid4())

    try:
        vector_store.add_chunks(document_id=document_id, chunks=chunks)
    except VectorStoreError as e:
        logger.error("Failed to index chunks into vector store for document '%s': %s", document_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document indexing failed: {e.message}",
        ) from e

    return DocumentUploadResponse(
        document_id=document_id,
        filename=filename,
        file_size_bytes=len(content),
        page_count=len(extracted_pages),
        total_chunks=len(chunks),
        pages=extracted_pages,
        chunks=chunks,
    )


@router.post(
    "/search",
    response_model=SearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Semantic search across document chunks",
    description="Retrieve the top-k most semantically relevant document chunks for a natural language query.",
)
def search_documents(
    payload: SearchRequest,
    vector_store: VectorStore = Depends(get_vector_store),
) -> SearchResponse:
    """Perform vector search on indexed document chunks."""
    query = payload.query.strip()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty.",
        )

    if payload.top_k <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="top_k must be greater than zero.",
        )

    try:
        results = vector_store.search(
            query=query,
            top_k=payload.top_k,
            document_id=payload.document_id,
        )
    except Exception as e:
        logger.error("Search query failed for query '%s': %s", query, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic search failed: {e}",
        ) from e

    return SearchResponse(
        query=query,
        results=results,
        total_results=len(results),
    )


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a document and its chunks from the vector store",
)
def delete_document(
    document_id: str,
    vector_store: VectorStore = Depends(get_vector_store),
) -> dict:
    """Delete a document's chunks from ChromaDB."""
    deleted_chunks = vector_store.delete_document(document_id=document_id)
    return {
        "status": "deleted",
        "document_id": document_id,
        "deleted_chunks": deleted_chunks,
    }

