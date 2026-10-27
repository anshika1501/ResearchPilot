"""Integration tests for the RAG question answering /chat endpoint."""

import io
import pytest
from fastapi.testclient import TestClient
import pymupdf

from app.api.deps import get_ollama_client
from app.core.config import settings
from app.llm.exceptions import (
    OllamaConnectionError,
    OllamaModelNotFoundError,
    OllamaTimeoutError,
)
from app.main import app


def create_in_memory_pdf(pages: list[str]) -> bytes:
    doc = pymupdf.open()
    for text in pages:
        page = doc.new_page()
        if text:
            page.insert_text((50, 72), text)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


class StubOllamaClient:
    def __init__(self, answer: str = "Default answer [Source: vector_guide.pdf, Page 1]"):
        self.answer = answer
        self.model = "mock-llama3.2"

    def generate(self, messages, temperature=None):
        return self.answer


def test_chat_grounded_answer_with_citations(client: TestClient):
    """Test standard grounded question answering flow returning citations and evidence."""
    pdf_bytes = create_in_memory_pdf(["ChromaDB manages dense embedding collections and cosine similarity."])
    files = {"file": ("vector_guide.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    upload_resp = client.post(f"{settings.API_V1_STR}/documents/upload", files=files)
    assert upload_resp.status_code == 200

    stub = StubOllamaClient("ChromaDB manages embedding collections [Source: vector_guide.pdf, Page 1].")
    app.dependency_overrides[get_ollama_client] = lambda: stub

    payload = {"question": "What does ChromaDB manage?"}
    response = client.post(f"{settings.API_V1_STR}/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["has_sufficient_evidence"] is True
    assert "ChromaDB manages embedding collections" in data["answer"]
    assert len(data["citations"]) >= 1
    assert data["citations"][0]["source_filename"] == "vector_guide.pdf"
    assert data["citations"][0]["page_number"] == 1
    assert len(data["evidence"]) >= 1
    assert "ChromaDB manages" in data["evidence"][0]["text"]


def test_chat_root_endpoint_compatibility(client: TestClient):
    """Test that POST /chat works at the root path as well."""
    pdf_bytes = create_in_memory_pdf(["FastAPI is a modern web framework for Python."])
    upload_resp = client.post("/documents/upload", files={"file": ("fastapi.pdf", io.BytesIO(pdf_bytes), "application/pdf")})
    assert upload_resp.status_code == 200

    stub = StubOllamaClient("FastAPI is a Python web framework [Source: fastapi.pdf, Page 1].")
    app.dependency_overrides[get_ollama_client] = lambda: stub

    response = client.post("/chat", json={"question": "What is FastAPI?"})
    assert response.status_code == 200
    assert response.json()["has_sufficient_evidence"] is True


def test_chat_with_no_retrieved_evidence(client: TestClient):
    """Test questioning a topic not covered in any uploaded document."""
    stub = StubOllamaClient("Should not be called")
    app.dependency_overrides[get_ollama_client] = lambda: stub

    # Search with a filter for a non-existent document ID
    payload = {
        "question": "What is quantum gravity?",
        "document_id": "nonexistent-doc-id",
    }
    response = client.post(f"{settings.API_V1_STR}/chat", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["has_sufficient_evidence"] is False
    assert "insufficient evidence" in data["answer"].lower()
    assert data["citations"] == []
    assert data["evidence"] == []


def test_chat_document_id_filter(client: TestClient):
    """Test filtering chat to a specific document."""
    pdf_1 = create_in_memory_pdf(["Apples are grown in orchards."])
    pdf_2 = create_in_memory_pdf(["Oranges are grown in groves."])

    r1 = client.post(f"{settings.API_V1_STR}/documents/upload", files={"file": ("apple.pdf", io.BytesIO(pdf_1), "application/pdf")})
    r2 = client.post(f"{settings.API_V1_STR}/documents/upload", files={"file": ("orange.pdf", io.BytesIO(pdf_2), "application/pdf")})
    doc_id_1 = r1.json()["document_id"]
    doc_id_2 = r2.json()["document_id"]

    stub = StubOllamaClient("Apples are grown in orchards [Source: apple.pdf, Page 1].")
    app.dependency_overrides[get_ollama_client] = lambda: stub

    response = client.post(
        f"{settings.API_V1_STR}/chat",
        json={"question": "Where are apples grown?", "document_id": doc_id_1},
    )
    assert response.status_code == 200
    data = response.json()
    for ev in data["evidence"]:
        assert ev["document_id"] == doc_id_1


def test_chat_empty_question_rejected(client: TestClient):
    """Test that empty questions return 400 or 422 Bad Request."""
    response = client.post(f"{settings.API_V1_STR}/chat", json={"question": "   "})
    assert response.status_code in (400, 422)


def test_chat_ollama_connection_error_handling(client: TestClient):
    """Test 503 error returned when Ollama is offline."""
    pdf_bytes = create_in_memory_pdf(["Some sample content."])
    client.post(f"{settings.API_V1_STR}/documents/upload", files={"file": ("doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")})

    class FailingOllamaClient:
        model = "test-model"
        def generate(self, messages, temperature=None):
            raise OllamaConnectionError("Ollama service unreachable at http://localhost:11434")

    app.dependency_overrides[get_ollama_client] = lambda: FailingOllamaClient()

    response = client.post(f"{settings.API_V1_STR}/chat", json={"question": "Sample question?"})
    assert response.status_code == 503
    assert "unreachable" in response.json()["detail"].lower()


def test_chat_ollama_timeout_error_handling(client: TestClient):
    """Test 504 error returned when Ollama times out."""
    pdf_bytes = create_in_memory_pdf(["Some sample content."])
    client.post(f"{settings.API_V1_STR}/documents/upload", files={"file": ("doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")})

    class TimeoutOllamaClient:
        model = "test-model"
        def generate(self, messages, temperature=None):
            raise OllamaTimeoutError("Ollama request timed out after 30s")

    app.dependency_overrides[get_ollama_client] = lambda: TimeoutOllamaClient()

    response = client.post(f"{settings.API_V1_STR}/chat", json={"question": "Sample question?"})
    assert response.status_code == 504
    assert "timed out" in response.json()["detail"].lower()


def test_chat_ollama_model_not_found_handling(client: TestClient):
    """Test 502 error returned when configured model is missing."""
    pdf_bytes = create_in_memory_pdf(["Some sample content."])
    client.post(f"{settings.API_V1_STR}/documents/upload", files={"file": ("doc.pdf", io.BytesIO(pdf_bytes), "application/pdf")})

    class MissingModelOllamaClient:
        model = "test-model"
        def generate(self, messages, temperature=None):
            raise OllamaModelNotFoundError("Model not found")

    app.dependency_overrides[get_ollama_client] = lambda: MissingModelOllamaClient()

    response = client.post(f"{settings.API_V1_STR}/chat", json={"question": "Sample question?"})
    assert response.status_code == 502
    assert "not found" in response.json()["detail"].lower()
