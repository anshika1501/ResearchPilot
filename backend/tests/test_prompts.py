"""Unit tests for RAG prompt construction."""

import pytest
from app.llm.prompts import build_rag_messages, SYSTEM_PROMPT
from app.schemas.documents import SearchResult


def test_system_prompt_enforces_safety_and_groundedness():
    """Verify system prompt instructs groundedness, citation format, and untrusted context rules."""
    assert "insufficient evidence" in SYSTEM_PROMPT.lower()
    assert "untrusted" in SYSTEM_PROMPT.lower()
    assert "cite" in SYSTEM_PROMPT.lower()


def test_build_rag_messages_with_passages():
    """Verify prompt formats context passages and question correctly."""
    passages = [
        SearchResult(
            text="ResearchPilot utilizes ChromaDB for vector retrieval.",
            source_filename="arch.pdf",
            page_number=2,
            chunk_index=0,
            document_id="doc-1",
            distance=0.15,
            metadata={},
        ),
        SearchResult(
            text="Sentence transformers produce 384-dimensional embeddings.",
            source_filename="arch.pdf",
            page_number=3,
            chunk_index=1,
            document_id="doc-1",
            distance=0.22,
            metadata={},
        ),
    ]

    question = "How are vectors retrieved in ResearchPilot?"
    messages = build_rag_messages(question=question, passages=passages)

    assert len(messages) == 2
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"

    user_content = messages[1]["content"]
    assert "arch.pdf" in user_content
    assert "Page: 2" in user_content or "Page 2" in user_content
    assert "Page: 3" in user_content or "Page 3" in user_content
    assert "ResearchPilot utilizes ChromaDB" in user_content
    assert question in user_content


def test_build_rag_messages_empty_passages():
    """Verify behavior when no passages are provided."""
    messages = build_rag_messages(question="What is the weather?", passages=[])
    assert len(messages) == 2
    assert "No context passages available" in messages[1]["content"]
