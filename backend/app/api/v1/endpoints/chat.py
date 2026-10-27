"""RAG chat and question answering endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_rag_service
from app.llm.exceptions import (
    LLMError,
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
)
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a grounded question about uploaded documents",
    description="Retrieve relevant passages from indexed documents and generate an evidence-backed answer with citations via Ollama.",
)
def chat_with_documents(
    payload: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> ChatResponse:
    """Generate a grounded answer to a user question using RAG."""
    question = payload.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty.",
        )

    try:
        return rag_service.answer_question(
            question=question,
            document_id=payload.document_id,
            top_k=payload.top_k,
        )
    except OllamaConnectionError as e:
        logger.error("Ollama connection error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=e.message,
        ) from e
    except OllamaTimeoutError as e:
        logger.error("Ollama timeout error: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=e.message,
        ) from e
    except OllamaModelNotFoundError as e:
        logger.error("Ollama model not found: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=e.message,
        ) from e
    except LLMError as e:
        logger.error("LLM error during answer generation: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error communicating with local LLM: {e.message}",
        ) from e
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
